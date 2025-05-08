import React, { useState, useEffect } from 'react';
import './Dialog.css';

const ItemOptionsDialog = ({ item, calculator, onSave, onCancel }) => {
  const [itemData, setItemData] = useState({ ...item });
  const [materialOptions, setMaterialOptions] = useState([]);
  const [selectedMaterial, setSelectedMaterial] = useState('');
  const [addOns, setAddOns] = useState({});
  const [previewPrices, setPreviewPrices] = useState({
    base: 0,
    material: 0,
    addons: 0,
    total: 0
  });

  // Initialize form data
  useEffect(() => {
    if (item) {
      setItemData({ ...item });
      
      // Set material options
      if (item.material?.options) {
        setMaterialOptions(item.material.options);
        setSelectedMaterial(item.material.selected || '');
      }
      
      // Set add-ons
      if (item.add_ons && typeof item.add_ons === 'object') {
        setAddOns(item.add_ons);
      } else {
        setAddOns({});
      }
      
      // Update preview
      updatePricePreview();
    }
  }, [item]);

  const updatePricePreview = () => {
    if (!calculator) return;
    
    // Calculate base amount (without material and add-ons)
    const baseItem = { ...itemData };
    
    // Reset material and add-ons for base calculation
    if (baseItem.material) {
      const baseMaterial = baseItem.material.base_material || 
                          (baseItem.material.options && baseItem.material.options[0]) || '';
      baseItem.material.selected = baseMaterial;
    }
    
    if (baseItem.add_ons && typeof baseItem.add_ons === 'object') {
      // Turn off all add-ons
      Object.keys(baseItem.add_ons).forEach(key => {
        baseItem.add_ons[key].selected = false;
      });
    }
    
    const baseAmount = calculator.calculateItemAmount(baseItem);
    
    // Calculate with material only
    const materialItem = { ...itemData };
    if (materialItem.add_ons && typeof materialItem.add_ons === 'object') {
      // Turn off all add-ons
      Object.keys(materialItem.add_ons).forEach(key => {
        materialItem.add_ons[key].selected = false;
      });
    }
    
    const materialAmount = calculator.calculateItemAmount(materialItem);
    const materialAddition = materialAmount - baseAmount;
    
    // Calculate full amount
    const fullAmount = calculator.calculateItemAmount(itemData);
    const addonsAmount = fullAmount - materialAmount;
    
    setPreviewPrices({
      base: baseAmount,
      material: materialAddition,
      addons: addonsAmount,
      total: fullAmount
    });
  };

  // Update item data when form changes
  useEffect(() => {
    updatePricePreview();
  }, [itemData, calculator]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    
    // Convert numeric values
    if (['length', 'height', 'quantity', 'rate'].includes(name)) {
      setItemData({
        ...itemData,
        [name]: parseFloat(value) || 0
      });
    } else {
      setItemData({
        ...itemData,
        [name]: value
      });
    }
  };

  const handleMaterialChange = (e) => {
    const selected = e.target.value;
    setSelectedMaterial(selected);
    
    // Update the material in item data
    setItemData({
      ...itemData,
      material: {
        ...itemData.material,
        selected
      }
    });
  };

  const handleAddOnChange = (name, checked) => {
    // Update the add-on in item data
    const updatedAddOns = { ...addOns };
    updatedAddOns[name] = {
      ...updatedAddOns[name],
      selected: checked
    };
    
    setAddOns(updatedAddOns);
    
    setItemData({
      ...itemData,
      add_ons: updatedAddOns
    });
  };

  const handleSave = () => {
    onSave(itemData);
  };

  // Helper function to get add-on price display
  const getAddOnPriceDisplay = (addOn) => {
    const ratePerUnit = addOn.rate_per_unit || 0;
    return `₹${ratePerUnit} per ${itemData.uom}`;
  };

  return (
    <div className="dialog-overlay">
      <div className="dialog">
        <div className="dialog-header">
          <h2>Item Options</h2>
        </div>
        
        <div className="dialog-content">
          <div className="tabs">
            <div className="tabs-header">
              <button className="tab-button active">Basic Info</button>
              <button className="tab-button">Materials</button>
              <button className="tab-button">Add-ons</button>
            </div>
            
            <div className="tab-content">
              <div className="basic-info-tab">
                <div className="form-group">
                  <label>Item:</label>
                  <input
                    type="text"
                    name="item"
                    value={itemData.item}
                    onChange={handleInputChange}
                  />
                </div>
                
                <div className="form-group">
                  <label>Unit of Measurement:</label>
                  <select 
                    name="uom"
                    value={itemData.uom}
                    onChange={handleInputChange}
                  >
                    <option value="SFT">Square Feet (SFT)</option>
                    <option value="RFT">Running Feet (RFT)</option>
                    <option value="NOS">Numbers (NOS)</option>
                  </select>
                </div>
                
                <div className="dimensions-group">
                  <h3>Dimensions</h3>
                  
                  <div className="form-group">
                    <label>Length:</label>
                    <input
                      type="number"
                      name="length"
                      value={itemData.length}
                      onChange={handleInputChange}
                      step="0.1"
                      min="0"
                    />
                  </div>
                  
                  {itemData.uom === 'SFT' && (
                    <div className="form-group">
                      <label>Height:</label>
                      <input
                        type="number"
                        name="height"
                        value={itemData.height}
                        onChange={handleInputChange}
                        step="0.1"
                        min="0"
                      />
                    </div>
                  )}
                  
                  <div className="form-group">
                    <label>Quantity:</label>
                    <input
                      type="number"
                      name="quantity"
                      value={itemData.quantity}
                      onChange={handleInputChange}
                      step="1"
                      min="1"
                    />
                  </div>
                  
                  <div className="form-group">
                    <label>Rate (₹):</label>
                    <input
                      type="number"
                      name="rate"
                      value={itemData.rate}
                      onChange={handleInputChange}
                      step="10"
                      min="0"
                    />
                  </div>
                </div>
                
                {/* Material options preview */}
                {materialOptions.length > 0 && (
                  <div className="material-preview">
                    <h3>Material Preview</h3>
                    <div className="form-group">
                      <label>Material:</label>
                      <select
                        value={selectedMaterial}
                        onChange={handleMaterialChange}
                      >
                        {materialOptions.map((option) => (
                          <option key={option} value={option}>{option}</option>
                        ))}
                      </select>
                    </div>
                  </div>
                )}
                
                {/* Add-ons preview */}
                {Object.keys(addOns).length > 0 && (
                  <div className="addons-preview">
                    <h3>Add-ons Preview</h3>
                    <div className="addon-list">
                      {Object.entries(addOns).slice(0, 2).map(([name, addon]) => (
                        <div key={name} className="addon-item">
                          <input
                            type="checkbox"
                            id={`addon-${name}`}
                            checked={addon.selected || false}
                            onChange={(e) => handleAddOnChange(name, e.target.checked)}
                          />
                          <label htmlFor={`addon-${name}`}>
                            {name} ({getAddOnPriceDisplay(addon)})
                          </label>
                        </div>
                      ))}
                      {Object.keys(addOns).length > 2 && (
                        <p>And {Object.keys(addOns).length - 2} more add-ons available...</p>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
          
          <div className="price-preview">
            <h3>Price Preview</h3>
            <div className="price-breakdown">
              <div className="price-row">
                <span>Base Price:</span>
                <span>₹{previewPrices.base.toFixed(2)}</span>
              </div>
              <div className="price-row">
                <span>Material Addition:</span>
                <span>₹{previewPrices.material.toFixed(2)}</span>
              </div>
              <div className="price-row">
                <span>Add-ons:</span>
                <span>₹{previewPrices.addons.toFixed(2)}</span>
              </div>
              <div className="price-row total">
                <span>Total Price:</span>
                <span>₹{previewPrices.total.toFixed(2)}</span>
              </div>
            </div>
          </div>
        </div>
        
        <div className="dialog-footer">
          <button onClick={handleSave} className="save-button">Save</button>
          <button onClick={onCancel} className="cancel-button">Cancel</button>
        </div>
      </div>
    </div>
  );
};

export default ItemOptionsDialog;