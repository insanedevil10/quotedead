export default ProjectInfoTab;import React, { useState, useEffect } from 'react';

const PROJECT_TYPES = ["Apartment", "Villa", "Farmhouse", "Independent House", "Office Space"];

// In a real application, these functions would communicate with a backend
const dummyAPI = {
  saveProject: (data) => new Promise(resolve => setTimeout(() => resolve(true), 500)),
  loadProject: () => new Promise(resolve => setTimeout(() => resolve({}), 500))
};

const ProjectInfoTab = ({ projectManager }) => {
  const [projectInfo, setProjectInfo] = useState({
    name: "",
    client_name: "",
    site_address: "",
    contact_info: "",
    project_type: PROJECT_TYPES[0]
  });

  const [statusMessage, setStatusMessage] = useState(null);

  // Load project info when component mounts
  useEffect(() => {
    const info = projectManager.getProjectInfo();
    setProjectInfo(info);
  }, [projectManager]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setProjectInfo(prevInfo => ({
      ...prevInfo,
      [name]: value
    }));
  };

  const handleSaveProject = async () => {
    // Update project info in the project manager
    projectManager.setProjectInfo(projectInfo);

    // Simulate saving to server/file
    setStatusMessage({ type: 'info', text: 'Saving project...' });
    
    try {
      await dummyAPI.saveProject(projectManager.getProjectData());
      setStatusMessage({ type: 'success', text: 'Project saved successfully!' });
    } catch (error) {
      setStatusMessage({ type: 'error', text: 'Error saving project.' });
    }
    
    setTimeout(() => setStatusMessage(null), 3000);
  };

  const handleLoadProject = async () => {
    // In a real app, this would open a file dialog
    setStatusMessage({ type: 'info', text: 'Loading project...' });
    
    try {
      const data = await dummyAPI.loadProject();
      // Normally we would load the project data here
      // For demo purposes, we'll just show a success message
      setStatusMessage({ type: 'success', text: 'Project loaded successfully!' });
    } catch (error) {
      setStatusMessage({ type: 'error', text: 'Error loading project.' });
    }
    
    setTimeout(() => setStatusMessage(null), 3000);
  };

  const handleNewProject = () => {
    if (window.confirm("Are you sure you want to create a new project? Unsaved changes will be lost.")) {
      // Reset project info
      const newProjectInfo = {
        name: "",
        client_name: "",
        site_address: "",
        contact_info: "",
        project_type: PROJECT_TYPES[0]
      };
      
      setProjectInfo(newProjectInfo);
      projectManager.setProjectInfo(newProjectInfo);
      
      setStatusMessage({ type: 'success', text: 'New project created!' });
      setTimeout(() => setStatusMessage(null), 3000);
    }
  };
  
  return (
    <div className="project-info-tab">
      <div className="card">
        <h2 className="card-header">Project Details</h2>
        
        <div className="form-group">
          <label htmlFor="project-name">Project Name:</label>
          <input
            type="text"
            id="project-name"
            name="name"
            value={projectInfo.name}
            onChange={handleInputChange}
            placeholder="Enter project name"
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="client-name">Client Name:</label>
          <input
            type="text"
            id="client-name"
            name="client_name"
            value={projectInfo.client_name}
            onChange={handleInputChange}
            placeholder="Enter client name"
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="site-address">Site Address:</label>
          <textarea
            id="site-address"
            name="site_address"
            value={projectInfo.site_address}
            onChange={handleInputChange}
            placeholder="Enter site address"
            rows="3"
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="contact-info">Contact Info:</label>
          <input
            type="text"
            id="contact-info"
            name="contact_info"
            value={projectInfo.contact_info}
            onChange={handleInputChange}
            placeholder="Enter contact information"
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="project-type">Project Type:</label>
          <select
            id="project-type"
            name="project_type"
            value={projectInfo.project_type}
            onChange={handleInputChange}
          >
            {PROJECT_TYPES.map((type) => (
              <option key={type} value={type}>{type}</option>
            ))}
          </select>
        </div>
        
        <div className="button-group">
          <button onClick={handleSaveProject}>Save Project</button>
          <button onClick={handleLoadProject}>Load Project</button>
          <button onClick={handleNewProject}>New Project</button>
        </div>
        
        {statusMessage && (
          <div className={`status-message status-${statusMessage.type}`}>
            {statusMessage.text}
          </div>
        )}
      </div>
      
      <div className="description mt-2">
        <p className="text-muted">
          Input your project details and client information here.
        </p>
      </div>
    </div>
    );
  };