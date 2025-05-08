import React, { useState, useEffect } from 'react';
import './Dialog.css';

const SelectFromRateCardDialog = ({ rateCardManager, calculator, onSave, onCancel }) => {
  const [categories, setCategories] = useState([]);
  const [rateCardItems, setRateCardItems] = useState([]);
  const [filteredItems, setFilteredItems] = useState([]);
  const [selectedItems, setSelectedItems] = useState([]);
  const [categoryFilter, setCategoryFilter] = useState('All Categories');
  const [uomFilter, setUomFilter] = useState('All');
  const [searchTerm, setSearchTerm] = useState('');

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

  // Apply filters when they change
  useEffect(() => {
    let filtered = [...rateCardItems];
    
    // Apply category filter
    if (categoryFilter !== 'All Categories') {
      filtered = filtered.filter(item => item.category === categoryFilter);
    }
    
    // Apply UOM filter
    if (uomFilter !== 'All') {
      filtered = filtered.filter(item => item.uom === uomFilter);
    }
    
    // Apply search filter
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(item => 
        item.item.toLowerCase().includes(term) || 
        item.category.toLowerCase().includes(term)
      );
    }
    
    setFilteredItems(filtered);
  }, [rateCardItems, categoryFilter, uomFilter, searchTerm]);

  const handleCategoryFilterChange = (e) => {
    setCategoryFilter(e.target.value);
  };

  const handleUomFilterChange = (e) => {
    setUomFilter(e.target.value);
  };

  const handleSearchChange = (e) => {
    setSearchTerm(e.target.value);
  };

  const handleAddItem = (item) => {
    // Convert rate card item to line item
    const lineItem = createItemFromRateCard(item);
    setSelectedItems([...selectedItems, lineItem]);
  };

  const handleRemoveItem = (index) => {
    const updatedItems = [...selectedItems];
    updatedItems.splice(index, 1);
    setSelectedItems(updatedItems);
  };

  const handleSave = () => {
    onSave(selectedItems);
  };

  // Helper function to create a line item from a rate card item
  const createItemFromRateCard = (rateCardItem) => {
    const item = {
      category: rateCardItem.category || "",
      item: rateCardItem.item || "",
      uom: rateCardItem.uom || "NOS",
      length: rateCardItem.uom === "SFT" || rateCardItem.uom === "RFT" ? 0 : "",
      height: rateCardItem.uom === "SFT" ? 0 : "",
      quantity: 1,
      rate: parseFloat(rateCardItem.rate || 0)
    };
    
    // Process material options if available and calculator exists
    if (rateCardItem.material_options && calculator) {
      const materialData = calculator.getMaterialOptionsFromRateCard({
        material_options: rateCardItem.material_options,
        material_prices: rateCardItem.material_prices || ""
      });
      
      if (materialData.options && materialData.options.length > 0) {
        item.material = materialData;
        if (materialData.base_material) {
          item.material.selected = materialData.base_material;
        }
      }
    }
    
    // Process add-ons if available and calculator exists
    if (rateCardItem.add_ons && rateCardItem.add_ons.toLowerCase() !== "none" && calculator) {
      const addOns = calculator.getAddOnsFromRateCard({
        add_ons: rateCardItem.add_ons,
        addon_prices: rateCardItem.addon_prices || ""
      });
      
      if (Object.keys(addOns).length > 0) {
        item.add_ons = addOns;
      }
    }
    
    // Calculate amount if calculator exists
    if (calculator) {
      item.amount = calculator.calculateItemAmount(item);
    } else {
      // Simple calculation if calculator not available
      item.amount = parseFloat(item.rate) * parseFloat(item.quantity || 1);
    }
    
    return item;
  };

  return (
    <div className="dialog-overlay">
      <div className="dialog rate-card-dialog">
        <div className="dialog-header">
          <h2>Select from Rate Card</h2>
        </div>
        
        <div className="dialog-content">
          <div className="rate-card-filter">
            <div className="filter-group">
              <label>Category:</label>
              <select value={categoryFilter} onChange={handleCategoryFilterChange}>
                <option>All Categories</option>
                {categories.map((category, index) => (
                  <option key={index} value={category}>{category}</option>
                ))}
              </select>
            </div>
            
            <div className="filter-group">
              <label>UOM:</label>
              <select value={uomFilter} onChange={handleUomFilterChange}>
                <option>All</option>
                <option>SFT</option>
                <option>RFT</option>
                <option>NOS</option>
              </select>
            </div>
            
            <div className="filter-group search-group">
              <label>Search:</label>
              <input
                type="text"
                value={searchTerm}
                onChange={handleSearchChange}
                placeholder="Search items..."
              />
            </div>
          </div>
          
          <div className="rate-card-items">
            <h3>Available Items ({filteredItems.length})</h3>
            
            {filteredItems.length === 0 ? (
              <p className="text-center">No items match the current filters</p>
            ) : (
              filteredItems.map((item, index) => (
                <div key={index} className="item-card">
                  <div className="item-card-details">
                    <div className="item-card-title">{item.item}</div>
                    <div className="item-card-subtitle">
                      {item.category} | {item.uom} | ₹{item.rate}
                    </div>
                  </div>
                  <div className="item-card-actions">
                    <button onClick={() => handleAddItem(item)}>Add</button>
                  </div>
                </div>
              ))
            )}
          </div>
          
          <div className="selected-items">
            <h3>Selected Items ({selectedItems.length})</h3>
            
            {selectedItems.length === 0 ? (
              <p className="text-center">No items selected yet</p>
            ) : (
              selectedItems.map((item, index) => (
                <div key={index} className="item-card">
                  <div className="item-card-details">
                    <div className="item-card-title">{item.item}</div>
                    <div className="item-card-subtitle">
                      {item.category} | {item.uom} | ₹{item.rate}
                    </div>
                  </div>
                  <div className="item-card-actions">
                    <button onClick={() => handleRemoveItem(index)}>Remove</button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
        
        <div className="dialog-footer">
          <button onClick={handleSave} className="save-button" disabled={selectedItems.length === 0}>
            Add {selectedItems.length} Items
          </button>
          <button onClick={onCancel} className="cancel-button">Cancel</button>
        </div>
      </div>
    </div>
  );
};

export default SelectFromRateCardDialog;