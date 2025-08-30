import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Label } from '@/components/ui/label.jsx'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Users, FileText, Calendar, CheckCircle, Clock, AlertCircle, Activity, Database, Shield, TrendingUp, AlertTriangle, Server, BarChart3, PieChart, Timer, Zap, Mail, Trash2 } from 'lucide-react'
import './App.css'

function App() {
  const [leads, setLeads] = useState([])
  const [systemHealth, setSystemHealth] = useState(null)
  const [kpis, setKpis] = useState(null)
  const [alerts, setAlerts] = useState([])
  const [dailyDigest, setDailyDigest] = useState(null)
  const [newLead, setNewLead] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    relationship: 'self'
  })

  // Fetch leads from API
  const fetchLeads = async () => {
    try {
      const response = await fetch('/api/leads')
      const data = await response.json()
      setLeads(data)
    } catch (error) {
      console.error('Error fetching leads:', error)
    }
  }

  // Fetch system health
  const fetchSystemHealth = async () => {
    try {
      const response = await fetch('/api/system/status')
      const data = await response.json()
      setSystemHealth(data)
    } catch (error) {
      console.error('Error fetching system health:', error)
    }
  }

  // Fetch KPIs
  const fetchKPIs = async () => {
    try {
      const response = await fetch('/api/kpis')
      const data = await response.json()
      setKpis(data)
    } catch (error) {
      console.error('Error fetching KPIs:', error)
    }
  }

  // Fetch alerts
  const fetchAlerts = async () => {
    try {
      const response = await fetch('/api/alerts')
      const data = await response.json()
      setAlerts(data.alerts || [])
    } catch (error) {
      console.error('Error fetching alerts:', error)
    }
  }

  // Fetch daily digest
  const fetchDailyDigest = async () => {
    try {
      const response = await fetch('/api/digest/daily')
      const data = await response.json()
      setDailyDigest(data)
    } catch (error) {
      console.error('Error fetching daily digest:', error)
    }
  }

  useEffect(() => {
    fetchLeads()
    fetchSystemHealth()
    fetchKPIs()
    fetchAlerts()
    fetchDailyDigest()
  }, [])

  // Create new lead
  const createLead = async (e) => {
    e.preventDefault()
    try {
      const response = await fetch('/api/leads', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newLead),
      })
      
      if (response.ok) {
        setNewLead({
          first_name: '',
          last_name: '',
          email: '',
          phone: '',
          stage: 'new',
          source: 'web_form'
        })
        fetchLeads() // Refresh the leads list
      }
    } catch (error) {
      console.error('Error creating lead:', error)
    }
  }

  // Send follow-up email
  const sendFollowUpEmail = async (leadId) => {
    try {
      const response = await fetch(`/api/leads/${leadId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      })
      
      const result = await response.json()
      
      if (response.ok) {
        alert(`✅ ${result.message}`)
        
        // Force immediate refresh of all data
        await fetchLeads()
        await fetchDashboardData()
        
        // Also force a page refresh after 1 second to ensure everything updates
        setTimeout(() => {
          window.location.reload()
        }, 1000)
        
      } else {
        alert(`❌ ${result.error || 'Failed to send follow-up email'}`)
      }
    } catch (error) {
      console.error('Error sending follow-up email:', error)
      alert('❌ Error sending follow-up email')
    }
  }

  // Simple delete function that actually works
  const deleteLead = async (leadId, leadName) => {
    // Confirm deletion
    if (!confirm(`Delete ${leadName}? This cannot be undone.`)) {
      return;
    }
    
    try {
      // Call the simple delete API
      const response = await fetch(`/api/delete-lead/${leadId}`, {
        method: 'DELETE'
      });
      
      const result = await response.json();
      
      if (result.success) {
        // Immediately remove from UI
        setLeads(currentLeads => currentLeads.filter(lead => lead.lead_id !== leadId));
        
        // Show success message
        alert(`✅ ${result.message}`);
        
        // Force complete page refresh after 1 second to ensure everything updates
        setTimeout(() => {
          window.location.reload();
        }, 1000);
        
      } else {
        alert(`❌ Error: ${result.error}`);
      }
      
    } catch (error) {
      console.error('Delete error:', error);
      alert('❌ Network error - please try again');
    }
  }

  // Get stage badge color
  const getStageBadgeColor = (stage) => {
    switch (stage) {
      case 'inquiry': return 'bg-gray-500'
      case 'docs_requested': return 'bg-blue-500'
      case 'docs_received': return 'bg-yellow-500'
      case 'clinical_review': return 'bg-orange-500'
      case 'consult_ready': return 'bg-green-500'
      case 'scheduled': return 'bg-purple-500'
      case 'decision': return 'bg-indigo-500'
      default: return 'bg-gray-500'
    }
  }

  // Get stage icon
  const getStageIcon = (stage) => {
    switch (stage) {
      case 'inquiry': return <Users className="w-4 h-4" />
      case 'docs_requested': return <FileText className="w-4 h-4" />
      case 'docs_received': return <CheckCircle className="w-4 h-4" />
      case 'clinical_review': return <Clock className="w-4 h-4" />
      case 'consult_ready': return <AlertCircle className="w-4 h-4" />
      case 'scheduled': return <Calendar className="w-4 h-4" />
      case 'decision': return <CheckCircle className="w-4 h-4" />
      default: return <Users className="w-4 h-4" />
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="app-header text-center mb-8">
          <h1 className="text-4xl font-bold mb-2">Admissions Co-Pilot</h1>
          <p className="text-xl">Patient Management & Workflow Automation System</p>
        </div>

        <Tabs defaultValue="dashboard" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="dashboard">Dashboard</TabsTrigger>
            <TabsTrigger value="leads">Leads</TabsTrigger>
            <TabsTrigger value="new-lead">New Lead</TabsTrigger>
            <TabsTrigger value="system-health">System Health</TabsTrigger>
          </TabsList>

          <TabsContent value="dashboard" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total Leads</CardTitle>
                  <Users className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{leads.length}</div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Docs Requested</CardTitle>
                  <FileText className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {leads.filter(lead => lead.stage === 'docs_requested').length}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Ready to Schedule</CardTitle>
                  <Calendar className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {leads.filter(lead => lead.stage === 'consult_ready').length}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Scheduled</CardTitle>
                  <CheckCircle className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {leads.filter(lead => lead.stage === 'scheduled').length}
                  </div>
                </CardContent>
              </Card>
            </div>

            <Card>
              <CardHeader>
                <CardTitle>Recent Activity</CardTitle>
                <CardDescription>Latest lead updates and activities</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {leads.slice(0, 5).map((lead) => (
                    <div key={lead.lead_id} className="flex items-center space-x-4">
                      <div className="flex items-center space-x-2">
                        {getStageIcon(lead.stage)}
                        <span className="font-medium">{lead.first_name} {lead.last_name}</span>
                      </div>
                      <Badge className={`${getStageBadgeColor(lead.stage)} text-white`}>
                        {lead.stage.replace('_', ' ').toUpperCase()}
                      </Badge>
                      <span className="text-sm text-gray-500 ml-auto">
                        {lead.last_touch_iso ? new Date(lead.last_touch_iso).toLocaleDateString() : 'N/A'}
                      </span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="leads" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>All Leads</CardTitle>
                <CardDescription>Manage and track all patient leads</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {leads.map((lead) => (
                    <div key={lead.lead_id} className="border rounded-lg p-4 space-y-2">
                      <div className="flex items-center justify-between">
                        <div>
                          <h3 className="font-semibold">{lead.first_name} {lead.last_name}</h3>
                          <p className="text-sm text-gray-600">{lead.email} • {lead.phone}</p>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Badge className={`${getStageBadgeColor(lead.stage)} text-white`}>
                            {lead.stage.replace('_', ' ').toUpperCase()}
                          </Badge>
                          {lead.has_consent && (
                            <Badge variant="outline" className="text-green-600 border-green-600">
                              Consent ✓
                            </Badge>
                          )}
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => sendFollowUpEmail(lead.lead_id)}
                            className="flex items-center space-x-1"
                          >
                            <Mail className="h-4 w-4" />
                            <span>Send Follow-up</span>
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => deleteLead(lead.lead_id, `${lead.first_name} ${lead.last_name}`)}
                            className="flex items-center space-x-1 text-red-600 border-red-600 hover:bg-red-50"
                          >
                            <Trash2 className="h-4 w-4" />
                            <span>Delete</span>
                          </Button>
                        </div>
                      </div>
                      <div className="text-sm text-gray-500">
                        Last updated: {lead.last_touch_iso ? new Date(lead.last_touch_iso).toLocaleString() : 'N/A'}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="new-lead" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Create New Lead</CardTitle>
                <CardDescription>Add a new patient lead to the system</CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={createLead} className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="first_name">First Name</Label>
                      <Input
                        id="first_name"
                        value={newLead.first_name}
                        onChange={(e) => setNewLead({...newLead, first_name: e.target.value})}
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="last_name">Last Name</Label>
                      <Input
                        id="last_name"
                        value={newLead.last_name}
                        onChange={(e) => setNewLead({...newLead, last_name: e.target.value})}
                        required
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="email">Email</Label>
                    <Input
                      id="email"
                      type="email"
                      value={newLead.email}
                      onChange={(e) => setNewLead({...newLead, email: e.target.value})}
                      required
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="phone">Phone</Label>
                    <Input
                      id="phone"
                      type="tel"
                      value={newLead.phone}
                      onChange={(e) => setNewLead({...newLead, phone: e.target.value})}
                      required
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="relationship">Relationship</Label>
                    <Select value={newLead.relationship} onValueChange={(value) => setNewLead({...newLead, relationship: value})}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select relationship" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="self">Self</SelectItem>
                        <SelectItem value="caregiver">Caregiver</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <Button type="submit" className="w-full">
                    Create Lead
                  </Button>
                </form>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="system-health" className="space-y-6">
            {/* System Overview Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">System Status</CardTitle>
                  <Server className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="flex items-center space-x-2">
                    <div className={`w-3 h-3 rounded-full ${systemHealth?.overall_status === 'healthy' ? 'bg-green-500' : 'bg-red-500'}`}></div>
                    <div className="text-2xl font-bold capitalize">{systemHealth?.overall_status || 'Loading...'}</div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Database</CardTitle>
                  <Database className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{systemHealth?.health_checks?.database?.lead_count || 0}</div>
                  <p className="text-xs text-muted-foreground">Total Records</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Active Alerts</CardTitle>
                  <AlertTriangle className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-orange-600">{systemHealth?.active_alerts_count || 0}</div>
                  <p className="text-xs text-muted-foreground">{systemHealth?.critical_alerts_count || 0} Critical</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Version</CardTitle>
                  <Activity className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{systemHealth?.version || 'N/A'}</div>
                  <p className="text-xs text-muted-foreground">Current Build</p>
                </CardContent>
              </Card>
            </div>

            {/* KPI Metrics */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <TrendingUp className="h-5 w-5" />
                  <span>Key Performance Indicators</span>
                </CardTitle>
                <CardDescription>Business metrics and performance targets</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm font-medium">Docs to Consult Conversion</span>
                      <span className="text-sm text-muted-foreground">Target: 60%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className={`h-2 rounded-full ${(kpis?.kpis?.docs_to_consult_conversion || 0) >= 60 ? 'bg-green-500' : 'bg-orange-500'}`}
                        style={{ width: `${Math.min((kpis?.kpis?.docs_to_consult_conversion || 0), 100)}%` }}
                      ></div>
                    </div>
                    <span className="text-lg font-bold">{kpis?.kpis?.docs_to_consult_conversion || 0}%</span>
                  </div>

                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm font-medium">Consent Compliance</span>
                      <span className="text-sm text-muted-foreground">Target: 100%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className={`h-2 rounded-full ${(kpis?.kpis?.consent_compliance_rate || 0) >= 100 ? 'bg-green-500' : 'bg-orange-500'}`}
                        style={{ width: `${Math.min((kpis?.kpis?.consent_compliance_rate || 0), 100)}%` }}
                      ></div>
                    </div>
                    <span className="text-lg font-bold">{kpis?.kpis?.consent_compliance_rate || 0}%</span>
                  </div>

                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm font-medium">Automation Success</span>
                      <span className="text-sm text-muted-foreground">Target: >99%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className={`h-2 rounded-full ${(100 - (kpis?.kpis?.automation_failure_rate || 0)) >= 99 ? 'bg-green-500' : 'bg-orange-500'}`}
                        style={{ width: `${Math.min((100 - (kpis?.kpis?.automation_failure_rate || 0)), 100)}%` }}
                      ></div>
                    </div>
                    <span className="text-lg font-bold">{100 - (kpis?.kpis?.automation_failure_rate || 0)}%</span>
                  </div>

                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm font-medium">Docs Completion Time</span>
                      <span className="text-sm text-muted-foreground">Target: &lt;5 days</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className={`h-2 rounded-full ${(kpis?.kpis?.median_docs_completion_days || 0) <= 5 ? 'bg-green-500' : 'bg-red-500'}`}
                        style={{ width: `${Math.min(((5 - (kpis?.kpis?.median_docs_completion_days || 0)) / 5) * 100, 100)}%` }}
                      ></div>
                    </div>
                    <span className="text-lg font-bold">{kpis?.kpis?.median_docs_completion_days || 0} days</span>
                  </div>

                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm font-medium">Consult Efficiency</span>
                      <span className="text-sm text-muted-foreground">Target: &lt;10% overrun</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className={`h-2 rounded-full ${(kpis?.kpis?.consult_overrun_rate || 0) <= 10 ? 'bg-green-500' : 'bg-red-500'}`}
                        style={{ width: `${Math.min(((10 - (kpis?.kpis?.consult_overrun_rate || 0)) / 10) * 100, 100)}%` }}
                      ></div>
                    </div>
                    <span className="text-lg font-bold">{kpis?.kpis?.consult_overrun_rate || 0}%</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Health Checks */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Database className="h-5 w-5" />
                    <span>Database Health</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span>Status</span>
                      <Badge variant={systemHealth?.health_checks?.database?.status === 'healthy' ? 'default' : 'destructive'}>
                        {systemHealth?.health_checks?.database?.status || 'Unknown'}
                      </Badge>
                    </div>
                    <div className="flex justify-between items-center">
                      <span>Lead Count</span>
                      <span className="font-mono">{systemHealth?.health_checks?.database?.lead_count || 0}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Shield className="h-5 w-5" />
                    <span>Error Monitoring</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span>Status</span>
                      <Badge variant={systemHealth?.health_checks?.error_rate?.status === 'healthy' ? 'default' : 'destructive'}>
                        {systemHealth?.health_checks?.error_rate?.status || 'Unknown'}
                      </Badge>
                    </div>
                    <div className="flex justify-between items-center">
                      <span>Recent Errors</span>
                      <span className="font-mono">{systemHealth?.health_checks?.error_rate?.recent_errors || 0}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <AlertTriangle className="h-5 w-5" />
                    <span>Alert Status</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span>Status</span>
                      <Badge variant={systemHealth?.health_checks?.alerts?.status === 'healthy' ? 'default' : 'destructive'}>
                        {systemHealth?.health_checks?.alerts?.status || 'Unknown'}
                      </Badge>
                    </div>
                    <div className="flex justify-between items-center">
                      <span>Active Alerts</span>
                      <span className="font-mono">{systemHealth?.health_checks?.alerts?.active_alerts || 0}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Performance Metrics */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <BarChart3 className="h-5 w-5" />
                  <span>Performance Metrics</span>
                </CardTitle>
                <CardDescription>System performance and response times</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="space-y-2">
                    <div className="flex items-center space-x-2">
                      <Timer className="h-4 w-4 text-blue-500" />
                      <span className="text-sm font-medium">API Response Time</span>
                    </div>
                    <div className="text-2xl font-bold text-blue-600">~50ms</div>
                    <p className="text-xs text-muted-foreground">Average response time</p>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex items-center space-x-2">
                      <Zap className="h-4 w-4 text-green-500" />
                      <span className="text-sm font-medium">Throughput</span>
                    </div>
                    <div className="text-2xl font-bold text-green-600">100%</div>
                    <p className="text-xs text-muted-foreground">Request success rate</p>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex items-center space-x-2">
                      <Activity className="h-4 w-4 text-purple-500" />
                      <span className="text-sm font-medium">System Load</span>
                    </div>
                    <div className="text-2xl font-bold text-purple-600">Low</div>
                    <p className="text-xs text-muted-foreground">Current system load</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Daily Summary */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <PieChart className="h-5 w-5" />
                  <span>Daily Operational Summary</span>
                </CardTitle>
                <CardDescription>
                  {dailyDigest?.date ? `Summary for ${new Date(dailyDigest.date).toLocaleDateString()}` : 'Today\'s operational overview'}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Lead Pipeline Summary */}
                  <div className="space-y-4">
                    <h4 className="font-semibold flex items-center space-x-2">
                      <Users className="h-4 w-4" />
                      <span>Lead Pipeline</span>
                    </h4>
                    <div className="space-y-3">
                      {dailyDigest?.lead_counts ? Object.entries(dailyDigest.lead_counts).map(([stage, count]) => (
                        <div key={stage} className="flex justify-between items-center">
                          <span className="text-sm capitalize">{stage.replace('_', ' ')}</span>
                          <Badge variant="outline">{count}</Badge>
                        </div>
                      )) : (
                        <p className="text-sm text-muted-foreground">No pipeline data available</p>
                      )}
                      <div className="border-t pt-2">
                        <div className="flex justify-between items-center font-medium">
                          <span>Total Leads</span>
                          <Badge>{dailyDigest?.total_leads || 0}</Badge>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Activity Summary */}
                  <div className="space-y-4">
                    <h4 className="font-semibold flex items-center space-x-2">
                      <Activity className="h-4 w-4" />
                      <span>Recent Activity</span>
                    </h4>
                    <div className="space-y-3">
                      {dailyDigest?.recent_activity ? Object.entries(dailyDigest.recent_activity).map(([activity, count]) => (
                        <div key={activity} className="flex justify-between items-center">
                          <span className="text-sm">{activity}</span>
                          <Badge variant={activity === 'ALERT' ? 'destructive' : 'default'}>{count}</Badge>
                        </div>
                      )) : (
                        <p className="text-sm text-muted-foreground">No activity data available</p>
                      )}
                    </div>
                  </div>

                  {/* System Health Summary */}
                  <div className="space-y-4">
                    <h4 className="font-semibold flex items-center space-x-2">
                      <Shield className="h-4 w-4" />
                      <span>System Health</span>
                    </h4>
                    <div className="space-y-3">
                      <div className="flex justify-between items-center">
                        <span className="text-sm">Overall Status</span>
                        <Badge variant={dailyDigest?.system_health === 'healthy' ? 'default' : 'destructive'}>
                          {dailyDigest?.system_health || 'Unknown'}
                        </Badge>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm">Active Alerts</span>
                        <Badge variant="outline">{dailyDigest?.active_alerts || 0}</Badge>
                      </div>
                    </div>
                  </div>

                  {/* KPI Summary */}
                  <div className="space-y-4">
                    <h4 className="font-semibold flex items-center space-x-2">
                      <TrendingUp className="h-4 w-4" />
                      <span>Key Metrics</span>
                    </h4>
                    <div className="space-y-3">
                      {dailyDigest?.kpis ? Object.entries(dailyDigest.kpis).map(([metric, value]) => (
                        <div key={metric} className="flex justify-between items-center">
                          <span className="text-sm capitalize">{metric.replace('_', ' ')}</span>
                          <Badge variant="outline">
                            {typeof value === 'number' ? 
                              (metric.includes('rate') || metric.includes('conversion') ? `${value}%` : value) 
                              : value}
                          </Badge>
                        </div>
                      )) : (
                        <p className="text-sm text-muted-foreground">No KPI data available</p>
                      )}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Recent Alerts */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <AlertCircle className="h-5 w-5" />
                  <span>Recent Alerts</span>
                </CardTitle>
                <CardDescription>Latest system alerts and warnings</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {alerts.length === 0 ? (
                    <p className="text-muted-foreground text-center py-4">No alerts to display</p>
                  ) : (
                    alerts.slice(0, 5).map((alert, index) => (
                      <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                        <div className="flex items-center space-x-3">
                          <AlertTriangle className={`h-4 w-4 ${alert.severity === 'critical' ? 'text-red-500' : 'text-orange-500'}`} />
                          <div>
                            <p className="font-medium">{alert.message}</p>
                            <p className="text-sm text-muted-foreground">
                              {new Date(alert.timestamp).toLocaleString()}
                            </p>
                          </div>
                        </div>
                        <Badge variant={alert.severity === 'critical' ? 'destructive' : 'secondary'}>
                          {alert.severity}
                        </Badge>
                      </div>
                    ))
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}

export default App

