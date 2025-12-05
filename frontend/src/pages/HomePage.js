import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useNavigate } from 'react-router-dom';
import { Loader2, Stars, Heart, Briefcase, Sparkles } from 'lucide-react';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const HomePage = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [prices, setPrices] = useState({});
  const [selectedReport, setSelectedReport] = useState('yearly_prediction');
  
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    gender: '',
    occupation: '',
    relationship_status: '',
    dob: '',
    tob: '',
    location: '',
    lat: 28.6139,
    lon: 77.2090,
  });

  useEffect(() => {
    fetchPricing();
  }, []);

  const fetchPricing = async () => {
    try {
      const response = await axios.get(`${API}/pricing`);
      const priceMap = {};
      response.data.forEach(p => {
        priceMap[p.report_type] = p.current_price_inr;
      });
      setPrices(priceMap);
    } catch (error) {
      console.error('Error fetching pricing:', error);
    }
  };

  const handleInputChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      // Step 1: Create user
      const userResponse = await axios.post(`${API}/users`, {
        name: formData.name,
        email: formData.email,
        birth_details: {
          dob: formData.dob,
          tob: formData.tob,
          lat: parseFloat(formData.lat),
          lon: parseFloat(formData.lon),
          location: formData.location,
          timezone: 5.5
        }
      });

      const userId = userResponse.data.user_id;

      // Step 2: Create transaction
      const transactionResponse = await axios.post(`${API}/transactions/create`, {
        user_id: userId,
        report_type: selectedReport,
        amount: prices[selectedReport]
      });

      const transactionId = transactionResponse.data.transaction_id;

      // Step 3: Mock payment verification
      await axios.post(`${API}/transactions/verify`, {
        transaction_id: transactionId,
        payment_success: true
      });

      toast.success('Payment verified! Generating your report...');

      // Step 4: Generate report
      const reportResponse = await axios.post(`${API}/reports/generate`, {
        user_id: userId,
        transaction_id: transactionId,
        report_type: selectedReport,
        birth_details: {
          dob: formData.dob,
          tob: formData.tob,
          lat: parseFloat(formData.lat),
          lon: parseFloat(formData.lon),
          location: formData.location,
          timezone: 5.5
        }
      });

      const reportId = reportResponse.data.report_id;

      toast.success('Report generation started! Redirecting...');
      
      // Navigate to report page
      setTimeout(() => {
        navigate(`/report/${reportId}`);
      }, 1500);

    } catch (error) {
      console.error('Error:', error);
      toast.error(error.response?.data?.detail || 'Failed to generate report');
    } finally {
      setLoading(false);
    }
  };

  const reportTypes = [
    {
      id: 'yearly_prediction',
      name: 'Yearly Prediction 2026',
      subtitle: 'The Compass',
      icon: <Stars className="w-6 h-6" />,
      description: 'Advanced structured report: The Diagnosis + 2026 Forecast + Astro-Prescription',
      features: ['Self-Discovery Blueprint', 'Topic-Wise Predictions', 'Precision Timing', 'Visual Timelines']
    },
    {
      id: 'retro_check',
      name: 'The Retro-Check',
      subtitle: 'Past Verification',
      icon: <Sparkles className="w-6 h-6" />,
      description: 'Verify accuracy by analyzing your past 18-24 months with precise transit analysis',
      features: ['Past 18-24 Months', 'Big Signal Transits', 'Real-World Validation', 'Pattern Recognition']
    },
    {
      id: 'love_marriage',
      name: 'Love & Marriage',
      subtitle: 'The Harmony',
      icon: <Heart className="w-6 h-6" />,
      description: 'Deep relationship analysis with precise timing and compatibility insights',
      features: ['Relationship DNA', 'Marriage Windows', 'Conflict Cycles', 'Partner Compatibility']
    },
    {
      id: 'career_job',
      name: 'Career & Job',
      subtitle: 'The Climber',
      icon: <Briefcase className="w-6 h-6" />,
      description: 'Career roadmap with promotion windows, risk periods, and growth opportunities',
      features: ['Promotion Timing', 'Job Change Windows', 'Income Cycles', 'Office Politics Strategy']
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50">
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        
        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center mb-4">
            <Sparkles className="w-8 h-8 text-purple-600 mr-2" />
            <h1 className="text-5xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
              Astro-Trust Engine
            </h1>
          </div>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            AI-Powered Vedic Astrology Reports with Mathematical Precision
          </p>
        </div>

        {/* Report Selection */}
        <div className="grid md:grid-cols-3 gap-6 mb-12">
          {reportTypes.map((report) => (
            <Card 
              key={report.id}
              className={`cursor-pointer transition-all duration-300 hover:shadow-2xl border-2 ${
                selectedReport === report.id 
                  ? 'border-purple-500 shadow-xl scale-105' 
                  : 'border-gray-200 hover:border-purple-300'
              }`}
              onClick={() => setSelectedReport(report.id)}
              data-testid={`report-card-${report.id}`}
            >
              <CardHeader>
                <div className="flex items-center justify-between mb-2">
                  <div className={`p-3 rounded-lg ${
                    selectedReport === report.id 
                      ? 'bg-purple-100 text-purple-600' 
                      : 'bg-gray-100 text-gray-600'
                  }`}>
                    {report.icon}
                  </div>
                  {prices[report.id] && (
                    <span className="text-2xl font-bold text-purple-600">
                      ₹{prices[report.id]}
                    </span>
                  )}
                </div>
                <CardTitle className="text-xl">{report.name}</CardTitle>
                <CardDescription className="font-semibold text-purple-600">
                  {report.subtitle}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600 mb-4">{report.description}</p>
                <ul className="space-y-1">
                  {report.features.map((feature, idx) => (
                    <li key={idx} className="text-xs text-gray-500 flex items-center">
                      <span className="mr-2">✓</span> {feature}
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Form */}
        <Card className="shadow-2xl border-2 border-purple-200">
          <CardHeader className="bg-gradient-to-r from-purple-50 to-pink-50">
            <CardTitle className="text-2xl">Enter Your Birth Details</CardTitle>
            <CardDescription>
              Accurate details ensure precise astrological calculations
            </CardDescription>
          </CardHeader>
          <CardContent className="p-6">
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <Label htmlFor="name">Full Name *</Label>
                  <Input
                    id="name"
                    name="name"
                    placeholder="Enter your full name"
                    value={formData.name}
                    onChange={handleInputChange}
                    required
                    data-testid="input-name"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    name="email"
                    type="email"
                    placeholder="your@email.com"
                    value={formData.email}
                    onChange={handleInputChange}
                    data-testid="input-email"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="dob">Date of Birth * (DD-MM-YYYY)</Label>
                  <Input
                    id="dob"
                    name="dob"
                    placeholder="15-08-1990"
                    value={formData.dob}
                    onChange={handleInputChange}
                    required
                    data-testid="input-dob"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="tob">Time of Birth * (HH:MM)</Label>
                  <Input
                    id="tob"
                    name="tob"
                    placeholder="14:30"
                    value={formData.tob}
                    onChange={handleInputChange}
                    required
                    data-testid="input-tob"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="location">Birth Location *</Label>
                  <Input
                    id="location"
                    name="location"
                    placeholder="New Delhi, India"
                    value={formData.location}
                    onChange={handleInputChange}
                    required
                    data-testid="input-location"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="lat">Latitude</Label>
                    <Input
                      id="lat"
                      name="lat"
                      type="number"
                      step="0.0001"
                      placeholder="28.6139"
                      value={formData.lat}
                      onChange={handleInputChange}
                      required
                      data-testid="input-lat"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="lon">Longitude</Label>
                    <Input
                      id="lon"
                      name="lon"
                      type="number"
                      step="0.0001"
                      placeholder="77.2090"
                      value={formData.lon}
                      onChange={handleInputChange}
                      required
                      data-testid="input-lon"
                    />
                  </div>
                </div>
              </div>

              <Button
                type="submit"
                className="w-full h-12 text-lg font-semibold bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
                disabled={loading}
                data-testid="generate-report-button"
              >
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                    Processing...
                  </>
                ) : (
                  <>
                    Generate Report • ₹{prices[selectedReport] || '---'}
                  </>
                )}
              </Button>

              <p className="text-sm text-center text-gray-500">
                🔒 Secure payment processing • 15-day follow-up support
              </p>
            </form>
          </CardContent>
        </Card>

        {/* Footer */}
        <div className="text-center mt-12 text-gray-500 text-sm">
          <p>Powered by Google Gemini AI • Mathematical calculations by VedicAstroAPI</p>
          <p className="mt-2">✨ Transparent pricing • No hidden charges • Instant delivery ✨</p>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
