import React, { useState } from 'react';

export const Tabs = ({ children }) => {
  const [activeTab, setActiveTab] = useState(0);

  return (
    <div className="tabs">
      <div className="tabs-header">
        {React.Children.map(children, (child, index) => {
          // Check if the child is a Tab component
          if (React.isValidElement(child) && child.type === Tab) {
            return (
              <button
                className={`tab-button ${activeTab === index ? 'active' : ''}`}
                onClick={() => setActiveTab(index)}
              >
                {child.props.title}
              </button>
            );
          }
          return null;
        })}
      </div>
      <div className="tab-content">
        {React.Children.toArray(children)[activeTab]}
      </div>
    </div>
  );
};

export const Tab = ({ children }) => {
  return children;
};