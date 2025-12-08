import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useNavigate } from 'react-router-dom';
import { Loader2, Stars, Heart, Briefcase, Sparkles, Check, MapPin, Clock, MessageSquare, FileText } from 'lucide-react';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const HomePage = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [prices, setPrices] = useState({});
  const [selectedReport, setSelectedReport] = useState('yearly_prediction');
  const [mode, setMode] = useState('reports'); // 'reports' or 'chat'
  
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    gender: '',
    occupation: '',
    relationship_status: '',
    dob: '',
    tob: '',
    tobInput: '', // Raw time input
    tobNormalized: '', // Normalized 24h format
    location: '',
    lat: null,
    lon: null,
    timezone: 5.5,
  });

  // City autocomplete state
  const [cityOpen, setCityOpen] = useState(false);
  const [citySearch, setCitySearch] = useState('');
  const [cityResults, setCityResults] = useState([]);
  const [selectedCity, setSelectedCity] = useState(null);
  const [loadingCities, setLoadingCities] = useState(false);

  // Time input state
  const [timeError, setTimeError] = useState('');

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

  // Handle city search
  useEffect(() => {
    if (citySearch.length >= 3) {
      const delaySearch = setTimeout(async () => {
        setLoadingCities(true);
        try {
          const response = await axios.get(`${API}/utils/search-cities`, {
            params: { query: citySearch, max_results: 10 }
          });
          setCityResults(response.data.cities || []);
        } catch (error) {
          console.error('City search error:', error);
          toast.error('Failed to search cities');
        } finally {
          setLoadingCities(false);
        }
      }, 300); // Debounce

      return () => clearTimeout(delaySearch);
    } else {
      setCityResults([]);
    }
  }, [citySearch]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (cityOpen && !event.target.closest('#city-input') && !event.target.closest('.absolute.z-50')) {
        setCityOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [cityOpen]);

  // Handle city selection
  const handleCitySelect = (city) => {
    console.log('City selected:', city);
    setSelectedCity(city);
    setCitySearch(city.display_name);
    setFormData({
      ...formData,
      location: city.display_name,
      lat: city.lat,
      lon: city.lon,
      timezone: city.timezone === 'Asia/Kolkata' ? 5.5 : 5.5 // Default to IST
    });
    setCityOpen(false);
    setCityResults([]);
    toast.success(`✓ Selected: ${city.name}, ${city.country}`);
  };

  // Handle time input with smart parsing
  const handleTimeInput = async (value) => {
    setFormData({ ...formData, tobInput: value });
    setTimeError('');

    if (value.length >= 2) {
      try {
        const response = await axios.post(`${API}/utils/parse-time`, {
          time_input: value
        });

        if (response.data.success) {
          setFormData({
            ...formData,
            tobInput: value,
            tobNormalized: response.data.normalized_time,
            tob: response.data.normalized_time
          });
          setTimeError('');
        } else {
          setTimeError(response.data.error_message);
          setFormData({ ...formData, tobInput: value, tob: '' });
        }
      } catch (error) {
        console.error('Time parsing error:', error);
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    // Validation
    if (!formData.tob || timeError) {
      toast.error('Please enter a valid time of birth');
      return;
    }

    if (!selectedCity) {
      toast.error('Please select your birth city from the dropdown');
      return;
    }

    try {
      // Step 1: Create user
      const userResponse = await axios.post(`${API}/users`, {
        name: formData.name,
        email: formData.email,
        gender: formData.gender || null,
        occupation: formData.occupation || null,
        relationship_status: formData.relationship_status || null,
        birth_details: {
          dob: formData.dob,
          tob: formData.tob, // Normalized 24h format
          lat: formData.lat,
          lon: formData.lon,
          location: formData.location,
          timezone: formData.timezone
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
          tob: formData.tob, // Normalized 24h format
          lat: formData.lat,
          lon: formData.lon,
          location: formData.location,
          timezone: formData.timezone
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
        <div className="text-center mb-8">
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

        {/* Mode Toggle */}
        <div className="flex justify-center mb-8">
          <Card className="inline-flex p-1 bg-white shadow-lg border-2 border-purple-200">
            <Button
              variant={mode === 'reports' ? 'default' : 'ghost'}
              className={`flex items-center gap-2 ${
                mode === 'reports'
                  ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white'
                  : 'text-gray-600 hover:text-purple-600'
              }`}
              onClick={() => setMode('reports')}
            >
              <FileText className="w-4 h-4" />
              Generate Report
            </Button>
            <Button
              variant={mode === 'chat' ? 'default' : 'ghost'}
              className={`flex items-center gap-2 ${
                mode === 'chat'
                  ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white'
                  : 'text-gray-600 hover:text-purple-600'
              }`}
              onClick={() => navigate('/chat')}
            >
              <MessageSquare className="w-4 h-4" />
              Chat with AI
            </Button>
          </Card>
        </div>

        {/* Report Selection (only show in reports mode) */}
        {mode === 'reports' && (
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
                  <Label htmlFor="email">Email (Optional)</Label>
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
                  <Label htmlFor="gender">Gender (Optional - helps with accurate analysis)</Label>
                  <Select value={formData.gender} onValueChange={(value) => setFormData({...formData, gender: value})}>
                    <SelectTrigger data-testid="input-gender">
                      <SelectValue placeholder="Select gender" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="male">Male</SelectItem>
                      <SelectItem value="female">Female</SelectItem>
                      <SelectItem value="non_binary">Non-binary</SelectItem>
                      <SelectItem value="prefer_not_to_say">Prefer not to say</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="occupation">Occupation (Optional)</Label>
                  <Input
                    id="occupation"
                    name="occupation"
                    placeholder="e.g., Software Engineer, Teacher"
                    value={formData.occupation}
                    onChange={handleInputChange}
                    data-testid="input-occupation"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="relationship_status">Relationship Status (Optional)</Label>
                  <Select value={formData.relationship_status} onValueChange={(value) => setFormData({...formData, relationship_status: value})}>
                    <SelectTrigger data-testid="input-relationship">
                      <SelectValue placeholder="Select status" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="single">Single</SelectItem>
                      <SelectItem value="in_relationship">In a Relationship</SelectItem>
                      <SelectItem value="engaged">Engaged</SelectItem>
                      <SelectItem value="married">Married</SelectItem>
                      <SelectItem value="divorced">Divorced</SelectItem>
                      <SelectItem value="widowed">Widowed</SelectItem>
                    </SelectContent>
                  </Select>
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
                  <Label htmlFor="tob" className="flex items-center gap-2">
                    <Clock className="w-4 h-4" />
                    Time of Birth * (Flexible Format)
                  </Label>
                  <Input
                    id="tob"
                    name="tobInput"
                    placeholder="e.g., 2:35 PM, 14:35, or 1435"
                    value={formData.tobInput}
                    onChange={(e) => handleTimeInput(e.target.value)}
                    className={timeError ? 'border-red-500' : ''}
                    required
                    data-testid="input-tob"
                  />
                  {timeError && (
                    <p className="text-xs text-red-600">{timeError}</p>
                  )}
                  {formData.tobNormalized && !timeError && (
                    <p className="text-xs text-green-600 flex items-center gap-1">
                      <Check className="w-3 h-3" /> 
                      Parsed as: {formData.tobNormalized}
                    </p>
                  )}
                  <p className="text-xs text-gray-500">
                    Accepts: 12-hour (2:35 PM), 24-hour (14:35), or compact (1435)
                  </p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="city-input" className="flex items-center gap-2">
                    <MapPin className="w-4 h-4" />
                    Birth Location * (Type to search)
                  </Label>
                  <div className="relative">
                    <Input
                      id="city-input"
                      placeholder="Type city name (min 3 letters)..."
                      value={citySearch}
                      onChange={(e) => setCitySearch(e.target.value)}
                      onFocus={() => setCityOpen(true)}
                      className={selectedCity ? 'border-green-500' : ''}
                      data-testid="city-input"
                    />
                    {citySearch.length >= 3 && cityOpen && (
                      <div className="absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-md shadow-lg max-h-60 overflow-auto">
                        {loadingCities && (
                          <div className="p-4 text-sm text-center text-gray-500">
                            <Loader2 className="w-4 h-4 animate-spin mx-auto mb-2" />
                            Searching cities...
                          </div>
                        )}
                        {!loadingCities && cityResults.length === 0 && (
                          <div className="p-4 text-sm text-center text-gray-500">
                            No cities found. Try different spelling.
                          </div>
                        )}
                        {!loadingCities && cityResults.length > 0 && (
                          <div>
                            {cityResults.map((city) => (
                              <div
                                key={city.id}
                                onClick={() => handleCitySelect(city)}
                                className="px-4 py-3 cursor-pointer hover:bg-purple-50 border-b border-gray-100 last:border-b-0"
                                data-testid={`city-option-${city.name}`}
                              >
                                <div className="flex items-start gap-2">
                                  <MapPin className="w-4 h-4 text-purple-600 mt-0.5 flex-shrink-0" />
                                  <div className="flex flex-col">
                                    <span className="font-medium text-gray-900">{city.name}</span>
                                    <span className="text-xs text-gray-500">
                                      {city.state && `${city.state}, `}{city.country}
                                    </span>
                                  </div>
                                </div>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                  {selectedCity && (
                    <div className="p-3 bg-green-50 border border-green-200 rounded-md">
                      <p className="text-sm text-green-800 flex items-center gap-2 font-medium">
                        <Check className="w-4 h-4" />
                        Selected: {selectedCity.display_name}
                      </p>
                      <p className="text-xs text-green-600 mt-1 ml-6">
                        Coordinates: {selectedCity.lat.toFixed(4)}°, {selectedCity.lon.toFixed(4)}°
                      </p>
                    </div>
                  )}
                  {!selectedCity && (
                    <p className="text-xs text-gray-500">
                      Start typing to search cities. Lat/long will be auto-determined.
                    </p>
                  )}
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
