import React, { useState, useEffect } from 'react';

const RateCardTab = ({ rateCardManager }) => {
  const [categories, setCategories] = useState([]);
  const [rateCardItems, setRateCardItems] = useState([]);
  const [filteredItems, setFilteredItems] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('All Categories');
  const [searchTerm, setSearchTerm] = useState('');
  const [showItemDialog, setShowItemDialog] = useState(false);
  const [currentItem, setCurrentItem] = useState(null);
  const [currentItemIndex, setCurrentItemIndex] = useState(-1);
  const [statusMessage, setStatusMessage] = useState(null);

  // Load categories and items when component mounts
  useEffect(() => {
    if (rateCardManager) {
      const allCategories = rateCardManager.getCategories();
      setCategories(allCategories);
      
      const allItems = rateCardManager.getItems();
      setRateCardItems(allItems);
      setFilteredItems(allItems);
    }
  }, [rateCardManager]);

  // Filter items when search term or category changes
  useEffect(() => {
    let filtered = [...rateCardItems];
    
    // Filter by category
    if (selectedCategory !== 'All Categories') {
      filtered = filtered.filter(item => item.category === selectedCategory);
    }
    
    // Filter by search term
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(item => 
        item.item.toLowerCase().includes(term) || 
        item.category.toLowerCase().includes(term)
      );
    }
    
    setFilteredItems(filtered);
  }, [rateCardItems, selectedCategory, searchTerm]);

  const handleCategorySelect = (category) => {
    setSelectedCategory(category);
  };

  const handleSearchChange = (e) => {
    setSearchTerm(e.target.value);
  };

  const handleAddItem = () => {
    // Create a new empty item
    const newItem = {
      category: selectedCategory !== 'All Categories' ? selectedCategory : categories[0] || 'General',
      item: "",
      uom: "SFT",
      rate: 0,
      material_options: "",
      material_prices: "",
      add_ons: "",
      addon_prices: ""
    };
    
    setCurrentItem(newItem);
    setCurrentItemIndex(-1);
    setShowItemDialog(true);
  };

  const handleEditItem = (index) => {
    const item = { ...filteredItems[index] };
    
    // Find the actual index in the original list
    const actualIndex = rateCardItems.findIndex(originalItem => 
      originalItem.category === item.category && originalItem.item === item.item
    );
    
    setCurrentItem(item);
    setCurrentItemIndex(actualIndex);
    setShowItemDialog(true);
  };

  const handleDeleteItem = (index) => {
    const item = filteredItems[index];
    
    if (window.confirm(`Are you sure you want to delete '${item.item}'?`)) {
      // Find the actual index in the original list
      const actualIndex = rateCardItems.findIndex(originalItem => 
        originalItem.category === item.category && originalItem.item === item.item
      );
      
      if (actualIndex !== -1) {
        rateCardManager.deleteItem(actualIndex);
        
        // Update local state
        const updatedItems = [...rateCardItems];
        updatedItems.splice(actualIndex, 1);
        setRateCardItems(updatedItems);
        
        // Update categories if needed
        updateCategories(updatedItems);
        
        setStatusMessage({ type: 'success', text: `Deleted ${item.item}` });
        setTimeout(() => setStatusMessage(null), 2000);
      }
    }
  };

  const handleItemDialogSave = (item) => {
    if (currentItemIndex === -1) {
      // Add new item
      rateCardManager.addItem(item);
      
      // Update local state
      const updatedItems = [...rateCardItems, item];
      setRateCardItems(updatedItems);
      
      // Update categories if needed
      updateCategories(updatedItems);
    } else {
      // Update existing item
      rateCardManager.updateItem(currentItemIndex, item);
      
      // Update local state
      const updatedItems = [...rateCardItems];
      updatedItems[currentItemIndex] = item;
      setRateCardItems(updatedItems);
      
      // Update categories if needed
      updateCategories(updatedItems);
    }
    
    setShowItemDialog(false);
    setStatusMessage({ type: 'success', text: `${currentItemIndex === -1 ? 'Added' : 'Updated'} item` });
    setTimeout(() => setStatusMessage(null), 2000);
  };

  const handleItemDialogCancel = () => {
    setShowItemDialog(false);
  };

  const updateCategories = (items) => {
    const uniqueCategories = [...new Set(items.map(item => item.category))];
    setCategories(uniqueCategories);
  };

  const handleImportRateCard = () => {
    // In a real app, this would open a file dialog
    setStatusMessage({ type: 'info', text: 'Import feature will be available in future version' });
    setTimeout(() => setStatusMessage(null), 3000);
  };

  const handleExportRateCard = () => {
    // In a real app, this would open a file dialog
    setStatusMessage({ type: 'info', text: 'Export feature will be available in future version' });
    setTimeout(() => setStatusMessage(null), 3000);
  };

  const handlePasswordProtect = () => {
    // In a real app, this would prompt for a password
    setStatusMessage({ type: 'info', text: 'Password protection will be available in future version' });
    setTimeout(() => setStatusMessage(null), 3000);
  };

  return (
    <div className="rate-card-tab">
      <div className="rate-card-container">
        <div className="category-sidebar card">
          <h3 className="card-header">Categories</h3>
          
          <div className="category-list">
            <div 
              className={`category-item ${selectedCategory === 'All Categories' ? 'active' : ''}`}
              onClick={() => handleCategorySelect('All Categories')}
            >
              All Categories
            </div>
            
            {categories.map((category, index) => (
              <div 
                key={index}
                className={`category-item ${selectedCategory === category ? 'active' : ''}`}
                onClick={() => handleCategorySelect(category)}
              >
                {category}
              </div>
            ))}
          </div>
          
          <div className="category-buttons">
            <button>Add Category</button>
            <button disabled={selectedCategory === 'All Categories'}>Delete Category</button>
          </div>
        </div>
        
        <div className="rate-card-content">
          <div className="rate-card-header">
            <div className="rate-card-title">
              <h3>Rate Card Items</h3>
            </div>
            
            <div className="rate-card-search">
              <input
                type="text"
                value={searchTerm}
                onChange={handleSearchChange}
                placeholder="Search items..."
              />
            </div>
          </div>
          
          <div className="rate-card-table-container">
            <table className="rate-card-table">
              <thead>
                <tr>
                  <th>Category</th>
                  <th>Item</th>
                  <th>UOM</th>
                  <th>Base Rate (₹)</th>
                  <th>Material Options</th>
                  <th>Add-ons</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredItems.length === 0 ? (
                  <tr>
                    <td colSpan="7" className="text-center">
                      {searchTerm 
                        ? 'No items match your search' 
                        : selectedCategory !== 'All Categories'
                        ? 'No items in this category'
                        : 'No items in the rate card. Add some items to get started.'}
                    </td>
                  </tr>
                ) : (
                  filteredItems.map((item, index) => (
                    <tr key={index}>
                      <td>{item.category}</td>
                      <td>{item.item}</td>
                      <td>{item.uom}</td>
                      <td>{item.rate}</td>
                      <td>{item.material_options}</td>
                      <td>{item.add_ons}</td>
                      <td>
                        <div className="button-group">
                          <button onClick={() => handleEditItem(index)}>Edit</button>
                          <button onClick={() => handleDeleteItem(index)}>Delete</button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
          
          <div className="rate-card-buttons">
            <button onClick={handleAddItem}>Add Item</button>
          </div>
        </div>
      </div>
      
      <div className="rate-card-io">
        <button onClick={handleImportRateCard}>Import Rate Card</button>
        <button onClick={handleExportRateCard}>Export Rate Card</button>
        <button onClick={handlePasswordProtect}>Password Protect</button>
      </div>
      
      {statusMessage && (
        <div className={`status-message status-${statusMessage.type} mt-2`}>
          {statusMessage.text}
        </div>
      )}
      
      {showItemDialog && (
        <div className="dialog-overlay">
          <div className="dialog">
            <div className="dialog-header">
              <h2>{currentItemIndex === -1 ? 'Add New Item' : 'Edit Item'}</h2>
            </div>
            
            <div className="dialog-content">
              <form>
                <div className="form-group">
                  <label>Category:</label>
                  <select 
                    value={currentItem.category} 
                    onChange={(e) => setCurrentItem({...currentItem, category: e.target.value})}
                  >
                    {categories.map((category, index) => (
                      <option key={index} value={category}>{category}</option>
                    ))}
                    <option value="New Category...">New Category...</option>
                  </select>
                </div>
                
                <div className="form-group">
                  <label>Item Name:</label>
                  <input 
                    type="text" 
                    value={currentItem.item} 
                    onChange={(e) => setCurrentItem({...currentItem, item: e.target.value})}
                    placeholder="Enter item name"
                  />
                </div>
                
                <div className="form-group">
                  <label>Unit of Measurement:</label>
                  <select 
                    value={currentItem.uom} 
                    onChange={(e) => setCurrentItem({...currentItem, uom: e.target.value})}
                  >
                    <option value="SFT">Square Feet (SFT)</option>
                    <option value="RFT">Running Feet (RFT)</option>
                    <option value="NOS">Numbers (NOS)</option>
                  </select>
                </div>
                
                <div className="form-group">
                  <label>Base Rate (₹):</label>
                  <input 
                    type="number" 
                    value={currentItem.rate} 
                    onChange={(e) => setCurrentItem({...currentItem, rate: parseFloat(e.target.value)})}
                    min="0"
                    step="10"
                  />
                </div>
                
                <div className="form-group">
                  <label>Material Options (comma separated):</label>
                  <input 
                    type="text" 
                    value={currentItem.material_options} 
                    onChange={(e) => setCurrentItem({...currentItem, material_options: e.target.value})}
                    placeholder="e.g. Laminate, Veneer, PU"
                  />
                </div>
                
                <div className="form-group">
                  <label>Material Prices (format: Name:Price,Name:Price):</label>
                  <input 
                    type="text" 
                    value={currentItem.material_prices} 
                    onChange={(e) => setCurrentItem({...currentItem, material_prices: e.target.value})}
                    placeholder="e.g. Laminate:0,Veneer:500,PU:800"
                  />
                </div>
                
                <div className="form-group">
                  <label>Add-ons (comma separated):</label>
                  <input 
                    type="text" 
                    value={currentItem.add_ons} 
                    onChange={(e) => setCurrentItem({...currentItem, add_ons: e.target.value})}
                    placeholder="e.g. Lights, Profile Door"
                  />
                </div>
                
                <div className="form-group">
                  <label>Add-on Prices (format: Name:Price,Name:Price):</label>
                  <input 
                    type="text" 
                    value={currentItem.addon_prices} 
                    onChange={(e) => setCurrentItem({...currentItem, addon_prices: e.target.value})}
                    placeholder="e.g. Lights:250,Profile Door:150"
                  />
                </div>
              </form>
            </div>
            
            <div className="dialog-footer">
              <button onClick={() => handleItemDialogSave(currentItem)} className="save-button">Save</button>
              <button onClick={handleItemDialogCancel} className="cancel-button">Cancel</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RateCardTab;