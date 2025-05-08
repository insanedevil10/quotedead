import React, { useState, useEffect } from 'react';
import { CompanyConfig } from '../utils/CompanyConfig';

const ExportTab = ({ projectManager }) => {
  const [templates, setTemplates] = useState([
    {
      name: "Standard Template",
      include_logo: true,
      include_company_details: true,
      include_images: false,
      include_terms: true,
      terms_text: "1. 50% advance payment before work begins.\n2. Balance payment on completion.\n3. Taxes as per government regulations.\n4. Delivery within 4-6 weeks from confirmation.",
      primary_color: CompanyConfig.PRIMARY_COLOR,
      header_text: "Interior Design Quote",
      footer_text: `Thank you for choosing ${CompanyConfig.COMPANY_NAME}`,
      font_family: "Arial",
      font_size: 10,
      layout_type: 2 // Detailed layout
    }
  ]);
  const [selectedTemplate, setSelectedTemplate] = useState(0);
  const [exportFormat, setExportFormat] = useState("Excel (.xlsx)");
  const [includeImages, setIncludeImages] = useState(false);
  const [includeCompanyDetails, setIncludeCompanyDetails] = useState(true);
  const [companyName, setCompanyName] = useState(CompanyConfig.COMPANY_NAME);
  const [companyAddress, setCompanyAddress] = useState(CompanyConfig.COMPANY_ADDRESS);
  const [companyContact, setCompanyContact] = useState(`${CompanyConfig.COMPANY_PHONE} | ${CompanyConfig.COMPANY_EMAIL} | ${CompanyConfig.COMPANY_WEBSITE}`);
  const [includeTerms, setIncludeTerms] = useState(true);
  const [termsText, setTermsText] = useState("1. 50% advance payment before work begins.\n2. Balance payment on completion.\n3. Taxes as per government regulations.\n4. Delivery within 4-6 weeks from confirmation.");
  const [showTemplateEditor, setShowTemplateEditor] = useState(false);
  const [previewHtml, setPreviewHtml] = useState('');
  const [statusMessage, setStatusMessage] = useState(null);

  // Load project data and update preview when component mounts or changes
  useEffect(() => {
    updatePreview();
  }, [
    projectManager, selectedTemplate, exportFormat, includeImages, 
    includeCompanyDetails, companyName, companyAddress, companyContact,
    includeTerms, termsText
  ]);

  const updatePreview = () => {
    const projectData = projectManager.getProjectData();
    const projectInfo = projectData.project_info;
    const rooms = projectData.rooms;
    const lineItems = projectData.line_items;
    const settings = projectData.settings;
    
    // Get current template
    const template = templates[selectedTemplate];
    
    // Get style options from template
    const primaryColor = template.primary_color;
    const fontFamily = template.font_family;
    const fontSize = template.font_size;
    const headerText = template.header_text;
    const footerText = template.footer_text;
    
    // Calculate totals
    let roomTotals = {};
    let subtotal = 0;
    
    // Group items by room and calculate room totals
    for (const item of lineItems) {
      const roomName = item.room;
      if (!roomTotals[roomName]) {
        roomTotals[roomName] = 0;
      }
      roomTotals[roomName] += item.amount;
      subtotal += item.amount;
    }
    
    // Calculate GST, discount, and grand total
    const gstAmount = subtotal * (settings.gst / 100);
    const discountAmount = subtotal * (settings.discount / 100);
    const grandTotal = subtotal + gstAmount - discountAmount;
    
    // Build HTML preview
    let html = `
    <html>
    <head>
      <style>
        body { 
          font-family: ${fontFamily}, sans-serif; 
          color: black; 
          font-size: ${fontSize}pt; 
          background-color: white;
          margin: 0;
          padding: 20px;
        }
        h1 { 
          color: ${primaryColor}; 
          text-align: center;
          margin-top: 20px;
          margin-bottom: 20px;
        }
        h2 { 
          color: ${primaryColor}; 
          margin-top: 30px;
          margin-bottom: 10px;
          border-bottom: 1px solid #ddd;
          padding-bottom: 5px;
        }
        h3 {
          margin-top: 20px;
          margin-bottom: 10px;
        }
        .header { 
          background-color: ${CompanyConfig.HEADER_BG_COLOR}; 
          padding: 15px; 
          text-align: center;
          margin-bottom: 20px;
        }
        .header h3 { 
          color: ${CompanyConfig.HEADER_TEXT_COLOR}; 
          margin: 5px 0;
        }
        .footer { 
          background-color: #f8f8f8; 
          padding: 10px; 
          text-align: center; 
          font-style: italic;
          margin-top: 30px;
        }
        table { 
          width: 100%; 
          border-collapse: collapse; 
          margin-top: 10px;
          margin-bottom: 20px;
        }
        th { 
          background-color: ${primaryColor}; 
          color: white; 
          text-align: left; 
          padding: 8px;
        }
        td { 
          border: 1px solid #ddd; 
          padding: 8px;
        }
        tr:nth-child(even) {
          background-color: #f9f9f9;
        }
        .total { 
          font-weight: bold;
        }
        .logo {
          max-width: 250px;
          margin: 0 auto;
          display: block;
        }
      </style>
    </head>
    <body>
    `;
    
    // Company details if enabled
    if (includeCompanyDetails) {
      html += `
      <div class="header">
        ${includeImages ? '<img src="/api/placeholder/250/100" alt="Company Logo" class="logo" />' : ''}
        <h3 style="color: ${CompanyConfig.HEADER_TEXT_COLOR};">${companyName}</h3>
        <p style="color: ${CompanyConfig.HEADER_TEXT_COLOR};">${companyAddress.replace(/\n/g, "<br />")}<br>${companyContact}</p>
      </div>
      `;
    }
    
    // Document title
    html += `<h1>${headerText}</h1>`;
    
    // Project details
    html += `
    <h2>Project Details</h2>
    <table>
      <tr><td><strong>Project Name:</strong></td><td>${projectInfo.name || '(Not specified)'}</td></tr>
      <tr><td><strong>Client Name:</strong></td><td>${projectInfo.client_name || '(Not specified)'}</td></tr>
      <tr><td><strong>Site Address:</strong></td><td>${projectInfo.site_address || '(Not specified)'}</td></tr>
      <tr><td><strong>Contact:</strong></td><td>${projectInfo.contact_info || '(Not specified)'}</td></tr>
      <tr><td><strong>Project Type:</strong></td><td>${projectInfo.project_type || '(Not specified)'}</td></tr>
    </table>
    `;
    
    // Check if there are any line items
    if (lineItems.length === 0) {
      html += "<p>No items added to quote yet.</p>";
    } else {
      // Group items by room
      const roomItems = {};
      for (const item of lineItems) {
        const room = item.room;
        if (!roomItems[room]) {
          roomItems[room] = [];
        }
        roomItems[room].push(item);
      }
      
      // Add each room with its items
      html += "<h2>Quote Details</h2>";
      
      for (const [room, items] of Object.entries(roomItems)) {
        html += `<h3>Room: ${room}</h3>`;
        html += `
        <table>
          <tr>
            <th>Item</th>
            <th>UOM</th>
            <th>Dimensions</th>
            <th>Quantity</th>
            <th>Material</th>
            <th>Rate (₹)</th>
            <th>Amount (₹)</th>
          </tr>
        `;
        
        let roomTotal = 0;
        for (const item of items) {
          // Format dimensions based on UOM
          let dimensions = "N/A";
          if (item.uom === "SFT") {
            dimensions = `${item.length} × ${item.height}`;
          } else if (item.uom === "RFT") {
            dimensions = `${item.length}`;
          }
          
          // Get material if available
          let material = "";
          if (item.material && item.material.selected) {
            material = item.material.selected;
          }
          
          html += `
          <tr>
            <td>${item.item}</td>
            <td>${item.uom}</td>
            <td>${dimensions}</td>
            <td>${item.quantity}</td>
            <td>${material}</td>
            <td>${item.rate}</td>
            <td>₹${item.amount.toFixed(2)}</td>
          </tr>
          `;
          roomTotal += item.amount;
        }
        
        html += `
          <tr class="total">
            <td colspan="6" style="text-align: right;"><strong>Room Total:</strong></td>
            <td><strong>₹${roomTotal.toFixed(2)}</strong></td>
          </tr>
        </table>
        `;
      }
      
      // Add summary
      html += `
      <h2>Quote Summary</h2>
      <table>
        <tr>
          <td>Subtotal:</td>
          <td>₹${subtotal.toFixed(2)}</td>
        </tr>
        <tr>
          <td>GST (${settings.gst}%):</td>
          <td>₹${gstAmount.toFixed(2)}</td>
        </tr>
        <tr>
          <td>Discount (${settings.discount}%):</td>
          <td>₹${discountAmount.toFixed(2)}</td>
        </tr>
        <tr class="total">
          <td><strong>Grand Total:</strong></td>
          <td><strong>₹${grandTotal.toFixed(2)}</strong></td>
        </tr>
      </table>
      `;
      
      // Terms and conditions if enabled
      if (includeTerms && termsText) {
        html += `
        <h2>Terms and Conditions</h2>
        <p>${termsText.replace(/\n/g, "<br />")}</p>
        `;
      }
      
      // Footer text if available
      if (footerText) {
        html += `
        <div class="footer">
          <p>${footerText}</p>
        </div>
        `;
      }
    }
    
    html += `
    </body>
    </html>
    `;
    
    // Set preview HTML
    setPreviewHtml(html);
  };

  const handleTemplateChange = (e) => {
    const templateIndex = parseInt(e.target.value, 10);
    setSelectedTemplate(templateIndex);
    
    // Update form with template settings
    const template = templates[templateIndex];
    setIncludeImages(template.include_images);
    setIncludeCompanyDetails(template.include_company_details);
    setIncludeTerms(template.include_terms);
    setTermsText(template.terms_text);
  };

  const handleExportQuote = () => {
    const projectData = projectManager.getProjectData();
    
    // Check if there's anything to export
    if (projectData.line_items.length === 0) {
      setStatusMessage({ type: 'error', text: 'No items to export. Add some items first.' });
      setTimeout(() => setStatusMessage(null), 3000);
      return;
    }
    
    // In a real app, this would call an API to generate and download the file
    setStatusMessage({ type: 'success', text: `Project exported to ${exportFormat.split(' ')[0]} successfully!` });
    setTimeout(() => setStatusMessage(null), 3000);
  };

  const handleCreateTemplate = () => {
    setShowTemplateEditor(true);
  };

  const handleEditTemplate = () => {
    setShowTemplateEditor(true);
  };

  const handleDeleteTemplate = () => {
    if (templates.length <= 1) {
      setStatusMessage({ type: 'error', text: 'Cannot delete the last template' });
      setTimeout(() => setStatusMessage(null), 3000);
      return;
    }
    
    if (window.confirm(`Are you sure you want to delete the template '${templates[selectedTemplate].name}'?`)) {
      const updatedTemplates = [...templates];
      updatedTemplates.splice(selectedTemplate, 1);
      setTemplates(updatedTemplates);
      setSelectedTemplate(0);
      
      setStatusMessage({ type: 'success', text: 'Template deleted successfully' });
      setTimeout(() => setStatusMessage(null), 3000);
    }
  };

  return (
    <div className="export-tab">
      <div className="export-options card">
        <h3 className="card-header">Export Options</h3>
        
        <div className="template-selection">
          <label>Template:</label>
          <div className="template-controls">
            <select value={selectedTemplate} onChange={handleTemplateChange}>
              {templates.map((template, index) => (
                <option key={index} value={index}>{template.name}</option>
              ))}
            </select>
            
            <button onClick={handleCreateTemplate}>New</button>
            <button onClick={handleEditTemplate}>Edit</button>
            <button onClick={handleDeleteTemplate}>Delete</button>
          </div>
        </div>
        
        <div className="logo-selection">
          <label>Company Logo:</label>
          <div className="logo-preview">
            <img src="/api/placeholder/250/100" alt="Company Logo" />
          </div>
          <button>Change Logo</button>
        </div>
        
        <div className="export-format">
          <label>Export Format:</label>
          <select value={exportFormat} onChange={e => setExportFormat(e.target.value)}>
            <option>Excel (.xlsx)</option>
            <option>PDF (.pdf)</option>
          </select>
        </div>
        
        <div className="additional-options">
          <div className="checkbox-option">
            <input
              type="checkbox"
              id="include-images"
              checked={includeImages}
              onChange={e => setIncludeImages(e.target.checked)}
            />
            <label htmlFor="include-images">Include Item Images in Quote</label>
          </div>
          
          <div className="checkbox-option">
            <input
              type="checkbox"
              id="include-company-details"
              checked={includeCompanyDetails}
              onChange={e => setIncludeCompanyDetails(e.target.checked)}
            />
            <label htmlFor="include-company-details">Include Company Details</label>
          </div>
        </div>
      </div>
      
      <div className="company-info card">
        <h3 className="card-header">Company Information</h3>
        
        <div className="form-group">
          <label>Company Name:</label>
          <input
            type="text"
            value={companyName}
            onChange={e => setCompanyName(e.target.value)}
          />
        </div>
        
        <div className="form-group">
          <label>Address:</label>
          <textarea
            value={companyAddress}
            onChange={e => setCompanyAddress(e.target.value)}
            rows="3"
          />
        </div>
        
        <div className="form-group">
          <label>Contact:</label>
          <input
            type="text"
            value={companyContact}
            onChange={e => setCompanyContact(e.target.value)}
          />
        </div>
      </div>
      
      <div className="terms-card card">
        <h3 className="card-header">Terms and Conditions</h3>
        
        <div className="checkbox-option">
          <input
            type="checkbox"
            id="include-terms"
            checked={includeTerms}
            onChange={e => setIncludeTerms(e.target.checked)}
          />
          <label htmlFor="include-terms">Include Terms and Conditions</label>
        </div>
        
        <textarea
          value={termsText}
          onChange={e => setTermsText(e.target.value)}
          rows="4"
          disabled={!includeTerms}
        />
      </div>
      
      <div className="export-buttons">
        <button onClick={handleExportQuote}>Export Quote</button>
        <button onClick={updatePreview}>Update Preview</button>
      </div>
      
      <div className="export-preview card">
        <h3 className="card-header">Export Preview</h3>
        <div className="preview-container">
          <iframe
            title="Export Preview"
            srcDoc={previewHtml}
            style={{ 
              width: '100%', 
              height: '500px', 
              border: '1px solid #444', 
              backgroundColor: 'white' 
            }}
          />
        </div>
      </div>
      
      {statusMessage && (
        <div className={`status-message status-${statusMessage.type} mt-2`}>
          {statusMessage.text}
        </div>
      )}
      
      {showTemplateEditor && (
        <div className="dialog-overlay">
          <div className="dialog">
            <div className="dialog-header">
              <h2>Edit Template</h2>
            </div>
            <div className="dialog-content">
              <p>Template editor will be available in future version.</p>
            </div>
            <div className="dialog-footer">
              <button onClick={() => setShowTemplateEditor(false)}>Close</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ExportTab;