import React, { useState, useEffect } from 'react';
import { useSearchParams, useLocation, useNavigate } from 'react-router-dom';
import { apiSimplified, formatPrice, trackEvent } from './utils';
import { colors, shadows } from './theme';
import ResponsiveHeader from './ResponsiveHeader';

/**
 * CheckoutScreen V2 - Razorpay payment flow with responsive layout
 */
export default function CheckoutScreen({ token, tierId: propTierId, scenarioIds = [], onSuccess, onBack, onTabChange, user }) {
  // Get tierId from props, URL params, or location state
  const [searchParams] = useSearchParams();
  const location = useLocation();
  const navigate = useNavigate();
  const tierId = propTierId || searchParams.get('tier') || location.state?.tierId;
  
  const [loading, setLoading] = useState(true);
  const [tier, setTier] = useState(null);
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState(null);
  const [errorType, setErrorType] = useState(null); // 'order', 'payment', 'verification'
  
  // Handle back navigation
  const handleBack = () => {
    if (onBack) {
      onBack();
    } else {
      navigate(-1);
    }
  };

  useEffect(() => {
    if (!tierId) {
      setError('No package selected. Please choose a package first.');
      setErrorType('order');
      setLoading(false);
      return;
    }
    
    const loadTierData = async () => {
      try {
        const response = await apiSimplified.get(`/tiers/${tierId}`, token);
        setTier(response.tier);
        trackEvent('checkout_started', { 
          tier_id: tierId, 
          total_amount_inr: response.tier?.price_inr,
          flow_version: 'v5'
        }, token);
      } catch (err) {
        setError(err.message);
        setErrorType('order');
      } finally {
        setLoading(false);
      }
    };
    loadTierData();
  }, [tierId, token]);

  // Load Razorpay script
  const loadRazorpayScript = () => {
    return new Promise((resolve) => {
      if (typeof window.Razorpay !== 'undefined') {
        resolve(true);
        return;
      }
      const script = document.createElement('script');
      script.src = 'https://checkout.razorpay.com/v1/checkout.js';
      script.onload = () => resolve(true);
      script.onerror = () => resolve(false);
      document.body.appendChild(script);
    });
  };

  const handlePayment = async () => {
    setProcessing(true);
    setError(null);
    setErrorType(null);

    try {
      // Load Razorpay script first
      const scriptLoaded = await loadRazorpayScript();
      if (!scriptLoaded) {
        throw new Error('Failed to load payment gateway. Please check your internet connection.');
      }

      // Create order
      const orderResponse = await apiSimplified.post('/checkout/create-order', {
        tier_id: tierId,
        scenario_ids: scenarioIds,
        intake_notes: '',
      }, token);

      if (!orderResponse.ok || !orderResponse.razorpay_order_id) {
        throw new Error('Failed to create order. Please try again.');
      }

      // Configure Razorpay
      const options = {
        key: orderResponse.key_id,
        amount: orderResponse.amount,
        currency: orderResponse.currency || 'INR',
        name: 'NIRO',
        description: `${tier?.name || 'Pack'} - ${tier?.validity_weeks} weeks`,
        order_id: orderResponse.razorpay_order_id,
        handler: async function (response) {
          try {
            // Verify payment
            const verifyResponse = await apiSimplified.post('/checkout/verify', {
              order_id: orderResponse.order_id,
              razorpay_payment_id: response.razorpay_payment_id,
              razorpay_order_id: response.razorpay_order_id,
              razorpay_signature: response.razorpay_signature,
            }, token);

            if (verifyResponse.ok && verifyResponse.plan_id) {
              trackEvent('purchase_completed', { 
                tier_id: tierId, 
                plan_id: verifyResponse.plan_id,
                total_amount_inr: tier?.price_inr,
                flow_version: 'v5'
              }, token);

              onSuccess(verifyResponse.plan_id);
            } else {
              throw new Error('Payment verification failed');
            }
          } catch (err) {
            trackEvent('purchase_failed', { 
              tier_id: tierId, 
              failure_reason: err.message,
              failure_stage: 'verification',
              flow_version: 'v5'
            }, token);
            setError('Payment verification failed. If money was deducted, please contact support.');
            setErrorType('verification');
            setProcessing(false);
          }
        },
        prefill: {},
        theme: {
          color: colors.teal.primary,
        },
        modal: {
          ondismiss: function () {
            trackEvent('purchase_cancelled', { 
              tier_id: tierId,
              flow_version: 'v5'
            }, token);
            setProcessing(false);
          },
          escape: true,
          animation: true,
        },
      };

      // Open Razorpay
      const rzp = new window.Razorpay(options);
      rzp.on('payment.failed', function (response) {
        trackEvent('purchase_failed', { 
          tier_id: tierId, 
          failure_reason: response.error?.description || 'Payment failed',
          failure_code: response.error?.code,
          failure_stage: 'payment',
          flow_version: 'v5'
        }, token);
        setError(response.error?.description || 'Payment failed. Please try again or use a different method.');
        setErrorType('payment');
        setProcessing(false);
      });
      rzp.open();
    } catch (err) {
      trackEvent('purchase_failed', { 
        tier_id: tierId, 
        failure_reason: err.message,
        failure_stage: 'order',
        flow_version: 'v5'
      }, token);
      setError(err.message);
      setErrorType('order');
      setProcessing(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: colors.background.primary }}>
        <div 
          className="w-12 h-12 border-4 rounded-full animate-spin" 
          style={{ borderColor: `${colors.teal.light}`, borderTopColor: colors.teal.primary }}
        />
      </div>
    );
  }

  if (!tier) {
    return (
      <div className="min-h-screen flex items-center justify-center p-6" style={{ backgroundColor: colors.background.primary }}>
        <div className="text-center">
          <p className="text-red-500 mb-4">{error || 'Package not found'}</p>
          <button onClick={handleBack} style={{ color: colors.teal.primary }} className="font-medium">Go back</button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen" style={{ backgroundColor: colors.background.primary }}>
      {/* Responsive Header */}
      <ResponsiveHeader
        title="Checkout"
        showBackButton={true}
        onBack={handleBack}
        onTabChange={onTabChange}
      />

      {/* Content Container - Centered max-width */}
      <div className="max-w-2xl mx-auto p-4 md:p-8">
        {/* Order Summary */}
        <div 
          className="rounded-2xl p-6 md:p-8 mb-6"
          style={{ 
            backgroundColor: '#ffffff', 
            border: `1px solid ${colors.ui.borderDark}`,
            boxShadow: shadows.sm,
          }}
        >
          <h2 className="text-lg md:text-xl font-semibold mb-4" style={{ color: colors.text.dark }}>Order Summary</h2>
          
          <div className="flex items-start justify-between mb-4">
            <div>
              <p className="font-medium md:text-lg" style={{ color: colors.text.dark }}>{tier.name}</p>
              <p className="text-sm md:text-base" style={{ color: colors.text.secondary }}>{tier.validity_weeks} weeks access</p>
            </div>
            <p className="text-xl md:text-2xl font-bold" style={{ color: colors.text.dark }}>{formatPrice(tier.price_inr)}</p>
          </div>
          
          <div className="border-t pt-4 space-y-2" style={{ borderColor: colors.ui.borderDark }}>
            {tier.features?.slice(0, 4).map((feature, idx) => (
              <p key={idx} className="text-sm md:text-base flex items-center" style={{ color: colors.text.secondary }}>
                <span className="mr-2" style={{ color: colors.teal.primary }}>✓</span>
                {feature}
              </p>
            ))}
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div 
            className="rounded-xl p-4 mb-6"
            style={{ backgroundColor: 'rgba(244,67,54,0.1)', border: '1px solid rgba(244,67,54,0.3)' }}
          >
            <div className="flex items-start">
              <span className="text-red-500 mr-2">⚠️</span>
              <div className="flex-1">
                <p className="text-sm md:text-base font-medium text-red-700">{error}</p>
                {errorType === 'verification' && (
                  <p className="text-xs md:text-sm mt-1 text-red-600">
                    Contact support at help@niro.ai with your transaction details.
                  </p>
                )}
              </div>
            </div>
            {(errorType === 'payment' || errorType === 'order') && (
              <button
                onClick={() => { setError(null); setErrorType(null); }}
                className="mt-3 text-sm font-medium underline text-red-600"
              >
                Dismiss and try again
              </button>
            )}
          </div>
        )}

        {/* Pay Button */}
        <button
          onClick={handlePayment}
          disabled={processing}
          className="w-full font-semibold py-4 md:py-5 rounded-xl text-base md:text-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed active:scale-[0.99] hover:shadow-md"
          style={{ 
            backgroundColor: colors.peach.primary,
            color: colors.text.dark,
            boxShadow: shadows.md,
          }}
          data-testid="pay-btn"
        >
          {processing ? (
            <span className="flex items-center justify-center">
              <span 
                className="w-5 h-5 border-2 rounded-full animate-spin mr-2"
                style={{ borderColor: colors.text.dark, borderTopColor: 'transparent' }}
              />
              Processing...
            </span>
          ) : (
            `Pay ${formatPrice(tier.price_inr)}`
          )}
        </button>

        <p className="text-center text-xs md:text-sm mt-4" style={{ color: colors.text.muted }}>
          🔒 Secure payment via Razorpay
        </p>

        {/* Payment Methods */}
        <div className="mt-6 text-center">
          <p className="text-xs md:text-sm mb-2" style={{ color: colors.text.muted }}>Accepted payment methods</p>
          <div className="flex items-center justify-center space-x-4 md:space-x-6 text-sm md:text-base" style={{ color: colors.text.muted }}>
            <span>💳 Cards</span>
            <span>🏦 UPI</span>
            <span>🏛️ Net Banking</span>
          </div>
        </div>
      </div>
    </div>
  );
}
