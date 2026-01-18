import React, { useState, useEffect } from 'react';
import { apiV2, formatPrice } from './utils';

/**
 * CheckoutScreen - Payment flow with real Razorpay integration
 */
export default function CheckoutScreen({ 
  token,
  packageId,
  selectedRemedyIds,
  recommendationId,
  onSuccess,
  onBack 
}) {
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [package_, setPackage] = useState(null);
  const [remedies, setRemedies] = useState([]);
  const [order, setOrder] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadData();
    loadRazorpayScript();
  }, [packageId]);

  const loadRazorpayScript = () => {
    if (document.getElementById('razorpay-script')) return;
    
    const script = document.createElement('script');
    script.id = 'razorpay-script';
    script.src = 'https://checkout.razorpay.com/v1/checkout.js';
    script.async = true;
    document.body.appendChild(script);
  };

  const loadData = async () => {
    try {
      // Load package
      const pkgResponse = await apiV2.get(`/catalog/packages/${packageId}`, token);
      if (pkgResponse.ok) {
        setPackage(pkgResponse.package);
        
        // Filter selected remedies from package's suggested remedies
        const selectedRemedies = pkgResponse.package.suggested_remedies?.filter(
          r => selectedRemedyIds.includes(r.remedy_id)
        ) || [];
        setRemedies(selectedRemedies);
      }

      // Create order
      const orderResponse = await apiV2.post('/checkout/create-order', {
        package_id: packageId,
        remedy_addon_ids: selectedRemedyIds,
        recommendation_id: recommendationId,
      }, token);

      if (orderResponse.ok) {
        setOrder(orderResponse);
      } else {
        setError('Failed to create order');
      }
    } catch (err) {
      setError('Failed to load checkout');
    } finally {
      setLoading(false);
    }
  };

  const handlePayment = async () => {
    if (!order || !window.Razorpay) {
      setError('Payment system not ready. Please refresh and try again.');
      return;
    }
    
    setProcessing(true);
    setError(null);

    try {
      // Get checkout options from order
      const options = {
        ...order.checkout_options,
        handler: async function(response) {
          // Verify payment with backend
          try {
            const verifyResponse = await apiV2.post('/checkout/verify', {
              order_id: order.order_id,
              razorpay_payment_id: response.razorpay_payment_id,
              razorpay_signature: response.razorpay_signature,
            }, token);

            if (verifyResponse.ok) {
              onSuccess(verifyResponse.plan_id);
            } else {
              setError('Payment verification failed. Please contact support.');
              setProcessing(false);
            }
          } catch (err) {
            setError('Payment verification failed. Please contact support.');
            setProcessing(false);
          }
        },
        modal: {
          ondismiss: function() {
            setProcessing(false);
          },
          escape: true,
          animation: true,
        },
        theme: {
          color: '#10b981', // Emerald color
        }
      };

      // Open Razorpay checkout
      const razorpay = new window.Razorpay(options);
      razorpay.on('payment.failed', function(response) {
        setError(`Payment failed: ${response.error.description}`);
        setProcessing(false);
      });
      razorpay.open();
    } catch (err) {
      setError('Payment failed. Please try again.');
      setProcessing(false);
    }
  };

  // Loading
  if (loading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="w-12 h-12 border-4 border-emerald-200 border-t-emerald-500 rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <div className="bg-white px-6 pt-12 pb-6 border-b border-slate-100">
        <button 
          onClick={onBack}
          className="text-slate-500 mb-4 flex items-center"
        >
          <span className="mr-2">←</span> Back
        </button>
        <h1 className="text-2xl font-semibold text-slate-900">Checkout</h1>
      </div>

      <div className="p-6 space-y-4 pb-40">
        {/* Order Summary */}
        <div className="bg-white rounded-2xl p-5 border border-slate-100">
          <h3 className="font-semibold text-slate-800 mb-4">Order Summary</h3>
          
          {/* Package */}
          <div className="flex items-start justify-between py-3 border-b border-slate-100">
            <div>
              <p className="font-medium text-slate-800">{package_?.name}</p>
              <p className="text-slate-500 text-sm">{package_?.duration_weeks}-week program</p>
              {package_?.includes_consultation && (
                <p className="text-emerald-600 text-sm mt-1">✓ Includes expert consultation</p>
              )}
            </div>
            <p className="font-semibold text-slate-800">{formatPrice(package_?.price_inr || 0)}</p>
          </div>
          
          {/* Remedy Add-Ons */}
          {remedies.length > 0 && (
            <div className="py-3 border-b border-slate-100">
              <p className="text-sm text-slate-500 mb-2">Remedy Add-Ons</p>
              {remedies.map(remedy => (
                <div key={remedy.remedy_id} className="flex items-center justify-between py-2">
                  <div className="flex items-center">
                    <span className="text-lg mr-2">✨</span>
                    <p className="text-slate-700 text-sm">{remedy.name}</p>
                  </div>
                  <p className="text-slate-700 text-sm">{formatPrice(remedy.price_inr)}</p>
                </div>
              ))}
            </div>
          )}
          
          {/* Breakdown */}
          {order?.breakdown && (
            <div className="py-3 border-b border-slate-100 space-y-2">
              <div className="flex justify-between text-sm text-slate-600">
                <span>Package</span>
                <span>{formatPrice(order.breakdown.package)}</span>
              </div>
              {order.breakdown.remedies > 0 && (
                <div className="flex justify-between text-sm text-slate-600">
                  <span>Remedies</span>
                  <span>{formatPrice(order.breakdown.remedies)}</span>
                </div>
              )}
            </div>
          )}
          
          {/* Total */}
          <div className="flex items-center justify-between pt-4">
            <p className="font-semibold text-slate-800">Total</p>
            <p className="text-2xl font-bold text-emerald-600">{formatPrice(order?.amount_inr || 0)}</p>
          </div>
        </div>

        {/* What's Included */}
        <div className="bg-white rounded-2xl p-5 border border-slate-100">
          <h3 className="font-semibold text-slate-800 mb-4">What's Included</h3>
          <div className="space-y-3">
            <div className="flex items-start">
              <span className="text-emerald-500 mr-3">✓</span>
              <div>
                <p className="text-slate-800 text-sm font-medium">{package_?.duration_weeks}-week structured program</p>
                <p className="text-slate-500 text-xs">{package_?.daily_commitment_minutes} mins/day commitment</p>
              </div>
            </div>
            {package_?.includes_consultation && (
              <div className="flex items-start">
                <span className="text-emerald-500 mr-3">✓</span>
                <div>
                  <p className="text-slate-800 text-sm font-medium">Expert consultation sessions</p>
                  <p className="text-slate-500 text-xs">Unlimited chat + video calls</p>
                </div>
              </div>
            )}
            <div className="flex items-start">
              <span className="text-emerald-500 mr-3">✓</span>
              <div>
                <p className="text-slate-800 text-sm font-medium">Self-guided tools & resources</p>
                <p className="text-slate-500 text-xs">Interactive exercises & daily tasks</p>
              </div>
            </div>
            {remedies.length > 0 && (
              <div className="flex items-start">
                <span className="text-emerald-500 mr-3">✓</span>
                <div>
                  <p className="text-slate-800 text-sm font-medium">{remedies.length} remedy add-on{remedies.length > 1 ? 's' : ''}</p>
                  <p className="text-slate-500 text-xs">Personalized astrological remedies</p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Secure Payment Note */}
        <div className="bg-gradient-to-r from-emerald-50 to-teal-50 rounded-2xl p-4 border border-emerald-100">
          <div className="flex items-center">
            <span className="text-2xl mr-3">🔒</span>
            <div>
              <p className="text-emerald-800 font-medium text-sm">100% Secure Payment</p>
              <p className="text-emerald-600 text-xs">Powered by Razorpay. Your payment details are encrypted.</p>
            </div>
          </div>
        </div>

        {/* Error */}
        {error && (
          <div className="bg-red-50 text-red-700 px-4 py-3 rounded-xl text-sm">
            {error}
          </div>
        )}
      </div>

      {/* Fixed CTA */}
      <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-slate-100 p-4 shadow-lg">
        <button
          onClick={handlePayment}
          disabled={processing || !order}
          className="w-full bg-gradient-to-r from-emerald-500 to-teal-600 text-white font-semibold py-4 rounded-xl disabled:opacity-50 hover:shadow-lg transition-all flex items-center justify-center"
        >
          {processing ? (
            <>
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
              Processing...
            </>
          ) : (
            <>Pay {formatPrice(order?.amount_inr || 0)}</>
          )}
        </button>
        <div className="flex items-center justify-center mt-3 text-slate-400 text-xs">
          <span className="mr-2">💳</span>
          <span>UPI • Cards • Net Banking • Wallets</span>
        </div>
      </div>
    </div>
  );
}
