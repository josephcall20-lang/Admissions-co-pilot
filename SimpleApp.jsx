// Simple delete function that actually works
const simpleDeleteLead = async (leadId, leadName) => {
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
};

export default simpleDeleteLead;

