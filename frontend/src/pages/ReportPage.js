import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useParams } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { Loader2, Download, MessageCircle, CheckCircle, Clock, AlertCircle } from 'lucide-react';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ReportPage = () => {
  const { reportId } = useParams();
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [question, setQuestion] = useState('');
  const [askingQuestion, setAskingQuestion] = useState(false);
  const [answers, setAnswers] = useState([]);

  useEffect(() => {
    fetchReport();
    const interval = setInterval(() => {
      if (report?.status !== 'completed' && report?.status !== 'failed') {
        fetchReport();
      }
    }, 3000); // Poll every 3 seconds

    return () => clearInterval(interval);
  }, [reportId]);

  const fetchReport = async () => {
    try {
      const response = await axios.get(`${API}/reports/${reportId}`);
      setReport(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching report:', error);
      toast.error('Failed to load report');
      setLoading(false);
    }
  };

  const handleAskQuestion = async () => {
    if (!question.trim()) return;

    setAskingQuestion(true);
    try {
      const response = await axios.post(`${API}/reports/clarify`, {
        report_id: reportId,
        question: question
      });

      setAnswers([...answers, {
        question: question,
        answer: response.data.answer
      }]);
      setQuestion('');
      toast.success('Question answered!');
    } catch (error) {
      console.error('Error asking question:', error);
      toast.error(error.response?.data?.detail || 'Failed to get answer');
    } finally {
      setAskingQuestion(false);
    }
  };

  const handleDownloadPDF = () => {
    if (report?.pdf_url) {
      const filename = report.pdf_url.split('/').pop();
      window.open(`${API}/reports/download/${filename}`, '_blank');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-16 h-16 animate-spin text-purple-600 mx-auto mb-4" />
          <p className="text-xl text-gray-600">Loading your report...</p>
        </div>
      </div>
    );
  }

  const getStatusDisplay = () => {
    switch (report?.status) {
      case 'pending':
        return {
          icon: <Clock className="w-6 h-6 text-yellow-500" />,
          text: 'Report Pending',
          color: 'text-yellow-600',
          bg: 'bg-yellow-50'
        };
      case 'processing':
        return {
          icon: <Loader2 className="w-6 h-6 animate-spin text-blue-500" />,
          text: 'Generating Your Report...',
          color: 'text-blue-600',
          bg: 'bg-blue-50'
        };
      case 'completed':
        return {
          icon: <CheckCircle className="w-6 h-6 text-green-500" />,
          text: 'Report Ready',
          color: 'text-green-600',
          bg: 'bg-green-50'
        };
      case 'failed':
        return {
          icon: <AlertCircle className="w-6 h-6 text-red-500" />,
          text: 'Report Generation Failed',
          color: 'text-red-600',
          bg: 'bg-red-50'
        };
      default:
        return {
          icon: <Clock className="w-6 h-6 text-gray-500" />,
          text: 'Unknown Status',
          color: 'text-gray-600',
          bg: 'bg-gray-50'
        };
    }
  };

  const statusDisplay = getStatusDisplay();

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50">
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent mb-2">
            Your Astro Report
          </h1>
          <p className="text-gray-600">Report ID: {reportId}</p>
        </div>

        {/* Status Card */}
        <Card className={`mb-8 border-2 ${statusDisplay.bg}`} data-testid="report-status-card">
          <CardContent className="p-6 flex items-center justify-between">
            <div className="flex items-center space-x-4">
              {statusDisplay.icon}
              <div>
                <p className={`text-lg font-semibold ${statusDisplay.color}`}>
                  {statusDisplay.text}
                </p>
                {report?.processing_time_seconds && (
                  <p className="text-sm text-gray-600">
                    Processed in {report.processing_time_seconds.toFixed(1)} seconds
                  </p>
                )}
              </div>
            </div>
            {report?.status === 'completed' && report?.pdf_url && (
              <Button
                onClick={handleDownloadPDF}
                className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
                data-testid="download-pdf-button"
              >
                <Download className="mr-2 h-4 w-4" />
                Download PDF
              </Button>
            )}
          </CardContent>
        </Card>

        {/* Processing Message */}
        {(report?.status === 'pending' || report?.status === 'processing') && (
          <Card className="mb-8 border-2 border-blue-200 bg-blue-50">
            <CardContent className="p-6">
              <h3 className="font-semibold text-blue-900 mb-3">What's happening right now:</h3>
              <ul className="space-y-2 text-sm text-blue-800">
                <li className="flex items-center">
                  <span className="mr-2">🤖</span> Gemini AI is analyzing your birth chart
                </li>
                <li className="flex items-center">
                  <span className="mr-2">🔢</span> Fetching precise planetary calculations from VedicAstroAPI
                </li>
                <li className="flex items-center">
                  <span className="mr-2">📝</span> Generating personalized insights and remedies
                </li>
                <li className="flex items-center">
                  <span className="mr-2">📄</span> Creating your Astro-Prescription PDF
                </li>
              </ul>
              <p className="mt-4 text-xs text-blue-600">
                This usually takes 15-25 seconds. Please don't close this page.
              </p>
            </CardContent>
          </Card>
        )}

        {/* Report Content */}
        {report?.status === 'completed' && report?.interpreted_text && (
          <Card className="mb-8 shadow-xl" data-testid="report-content-card">
            <CardHeader className="bg-gradient-to-r from-purple-50 to-pink-50">
              <CardTitle className="text-2xl">Your Astrological Analysis</CardTitle>
              <CardDescription>
                {report.report_type === 'yearly_prediction' && 'Yearly Prediction (The Compass)'}
                {report.report_type === 'love_marriage' && 'Love & Marriage (The Harmony)'}
                {report.report_type === 'career_job' && 'Career & Job (The Climber)'}
              </CardDescription>
            </CardHeader>
            <CardContent className="p-6 prose prose-purple max-w-none">
              <div className="whitespace-pre-wrap text-gray-700 leading-relaxed">
                {report.interpreted_text}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Error Display */}
        {report?.status === 'failed' && (
          <Card className="mb-8 border-2 border-red-200 bg-red-50">
            <CardContent className="p-6">
              <h3 className="font-semibold text-red-900 mb-2">Report Generation Failed</h3>
              <p className="text-sm text-red-800 mb-4">
                {report?.code_execution_error || 'An error occurred while generating your report.'}
              </p>
              <p className="text-xs text-red-600">
                Please contact support with your Report ID: {reportId}
              </p>
            </CardContent>
          </Card>
        )}

        {/* Follow-up Questions */}
        {report?.status === 'completed' && (
          <Card className="shadow-xl">
            <CardHeader className="bg-gradient-to-r from-purple-50 to-pink-50">
              <CardTitle className="flex items-center">
                <MessageCircle className="mr-2 h-5 w-5" />
                Ask Follow-up Questions
              </CardTitle>
              <CardDescription>
                Get clarifications about your report (15-day support window)
              </CardDescription>
            </CardHeader>
            <CardContent className="p-6">
              <div className="space-y-4">
                <Textarea
                  placeholder="Ask any questions about your report..."
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  rows={3}
                  data-testid="question-input"
                />
                <Button
                  onClick={handleAskQuestion}
                  disabled={askingQuestion || !question.trim()}
                  className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
                  data-testid="ask-question-button"
                >
                  {askingQuestion ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Getting Answer...
                    </>
                  ) : (
                    'Ask Question'
                  )}
                </Button>
              </div>

              {/* Answers */}
              {answers.length > 0 && (
                <div className="mt-8 space-y-6" data-testid="answers-container">
                  {answers.map((qa, index) => (
                    <div key={index} className="border-l-4 border-purple-500 pl-4">
                      <p className="font-semibold text-gray-900 mb-2">
                        Q: {qa.question}
                      </p>
                      <p className="text-gray-700 whitespace-pre-wrap">
                        A: {qa.answer}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};

export default ReportPage;
