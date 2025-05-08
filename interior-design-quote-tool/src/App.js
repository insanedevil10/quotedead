import React, { useState, useEffect } from 'react';
import { Tabs, Tab } from './components/Tabs';
import ProjectInfoTab from './components/ProjectInfoTab';
import RoomsTab from './components/RoomsTab';
import ScopeOfWorkTab from './components/ScopeOfWorkTab';
import DashboardTab from './components/DashboardTab';
import ExportTab from './components/ExportTab';
import RateCardTab from './components/RateCardTab';
import { CompanyConfig } from './utils/CompanyConfig';
import './App.css';

const App = () => {
  // Initialize core state
  const [projectData, setProjectData] = useState({
    project_info: {
      name: "",
      client_name: "",
      site_address: "",
      contact_info: "",
      project_type: ""
    },
    rooms: [],
    line_items: [],
    settings: {
      gst: 18,
      discount: 0
    }
  });

  const [rateCardItems, setRateCardItems] = useState([]);

  // Load dummy rate card data
  useEffect(() => {
    setRateCardItems([
      {"category": "Wall Work", "item": "POP Wall", "uom": "SFT", "rate": 150, "material_options": "Standard, Premium", "add_ons": "None"},
      {"category": "Wall Work", "item": "Wall Painting", "uom": "SFT", "rate": 80, "material_options": "Regular, Texture", "add_ons": "None"},
      {"category": "Furniture", "item": "TV Unit", "uom": "SFT", "rate": 1200, "material_options": "Laminate, Veneer, PU", "add_ons": "Lights, Profile Door"},
      {"category": "Furniture", "item": "Wardrobe", "uom": "SFT", "rate": 1500, "material_options": "Laminate, Veneer, PU", "add_ons": "Lights, Profile Door"},
      {"category": "Furniture", "item": "Kitchen", "uom": "SFT", "rate": 2200, "material_options": "Laminate, Acrylic, PU", "add_ons": "Lights, Profile Door"},
      {"category": "Decorative", "item": "False Ceiling", "uom": "SFT", "rate": 220, "material_options": "Regular, Cove", "add_ons": "Lights"},
      {"category": "Decorative", "item": "Curtains", "uom": "SFT", "rate": 180, "material_options": "Regular, Blackout", "add_ons": "None"},
    ]);
  }, []);

  // Calculator functions
  const calculateItemAmount = (item) => {
    // Get base values
    const uom = item.uom || "NOS";
    const length = parseFloat(item.length || 0);
    const height = parseFloat(item.height || 0);
    const quantity = parseFloat(item.quantity || 0);
    const rate = parseFloat(item.rate || 0);
    
    // Calculate base amount based on UOM
    let baseAmount = 0;
    if (uom === "SFT") { // Square feet
      // Area calculation: length × height
      const area = length * height;
      baseAmount = area * quantity * rate;
    } else if (uom === "RFT") { // Running feet
      // Linear calculation: length only
      baseAmount = length * quantity * rate;
    } else if (uom === "NOS") { // Numbers/count
      // Just quantity × rate
      baseAmount = quantity * rate;
    } else {
      baseAmount = quantity * rate;
    }
    
    // Apply material additional cost if specified
    let totalAmount = baseAmount;
    let materialAddition = 0;
    
    if (item.material && item.material.selected) {
      const selectedMaterial = item.material.selected;
      const priceAdditions = item.material.price_additions || {};
      
      // Get price addition for selected material (default to 0 if not found)
      if (selectedMaterial in priceAdditions) {
        // Calculate additional cost based on UOM
        if (uom === "SFT") {
          materialAddition = priceAdditions[selectedMaterial] * length * height * quantity;
        } else if (uom === "RFT") {
          materialAddition = priceAdditions[selectedMaterial] * length * quantity;
        } else { // NOS
          materialAddition = priceAdditions[selectedMaterial] * quantity;
        }
      }
      
      // Add material cost to total
      totalAmount += materialAddition;
    }
    
    // Calculate add-on costs
    let addOnCost = 0;
    if (item.add_ons && typeof item.add_ons === 'object') {
      // Process each add-on
      for (const [addOnName, addOnInfo] of Object.entries(item.add_ons)) {
        // Skip if not selected
        if (!addOnInfo.selected) continue;
        
        // Get add-on rate
        const addOnRate = parseFloat(addOnInfo.rate_per_unit || 0);
        
        // Calculate add-on cost based on UOM
        if (uom === "SFT") {
          // For SFT, apply to the total square footage
          addOnCost += addOnRate * length * height * quantity;
        } else if (uom === "RFT") {
          // For RFT, apply to the total running feet
          addOnCost += addOnRate * length * quantity;
        } else {
          // For NOS, apply to the quantity
          addOnCost += addOnRate * quantity;
        }
      }
    }
    // Legacy support for string-based add-ons
    else if (item.add_ons && typeof item.add_ons === 'string' && item.add_ons) {
      const addOnNames = item.add_ons.split(',').map(x => x.trim().toLowerCase());
      
      // Process legacy string-based add-ons
      for (const addOn of addOnNames) {
        if (addOn === "profile door") {
          // Profile door: Additional ₹150 per SFT
          if (uom === "SFT") {
            addOnCost += 150 * length * height * quantity;
          }
        } else if (addOn === "lights") {
          // Lights: Additional ₹250 per SFT
          if (uom === "SFT") {
            addOnCost += 250 * length * height * quantity;
          }
        }
      }
    }
    
    // Add add-on cost to total
    totalAmount += addOnCost;
    
    return totalAmount;
  };

  const calculateRoomTotals = (lineItems) => {
    const roomTotals = {};
    for (const item of lineItems) {
      const room = item.room;
      const amount = item.amount || 0;
      
      if (!roomTotals[room]) {
        roomTotals[room] = 0;
      }
      
      roomTotals[room] += amount;
    }
    
    return roomTotals;
  };

  const calculateSubtotal = (roomTotals) => {
    return Object.values(roomTotals).reduce((sum, amount) => sum + amount, 0);
  };

  const calculateGST = (subtotal, gstPercent) => {
    return subtotal * (gstPercent / 100);
  };

  const calculateDiscount = (subtotal, discountPercent) => {
    return subtotal * (discountPercent / 100);
  };

  const calculateGrandTotal = (subtotal, gstAmount, discountAmount) => {
    return subtotal + gstAmount - discountAmount;
  };

  // Project management functions
  const updateProject = (newData) => {
    setProjectData(prevData => ({
      ...prevData,
      ...newData
    }));
  };

  const updateProjectInfo = (info) => {
    setProjectData(prevData => ({
      ...prevData,
      project_info: {
        ...prevData.project_info,
        ...info
      }
    }));
  };

  const addRoom = (room) => {
    setProjectData(prevData => ({
      ...prevData,
      rooms: [...prevData.rooms, room]
    }));
  };

  const deleteRoom = (index) => {
    const roomName = projectData.rooms[index].name;
    
    // Remove room from rooms list
    const updatedRooms = [...projectData.rooms];
    updatedRooms.splice(index, 1);
    
    // Remove associated line items
    const updatedLineItems = projectData.line_items.filter(
      item => item.room !== roomName
    );
    
    setProjectData(prevData => ({
      ...prevData,
      rooms: updatedRooms,
      line_items: updatedLineItems
    }));
  };

  const addLineItem = (item) => {
    // Calculate the amount
    const itemWithAmount = {
      ...item,
      amount: calculateItemAmount(item)
    };
    
    setProjectData(prevData => ({
      ...prevData,
      line_items: [...prevData.line_items, itemWithAmount]
    }));
  };

  const updateLineItem = (index, item) => {
    // Calculate the amount
    const itemWithAmount = {
      ...item,
      amount: calculateItemAmount(item)
    };
    
    const updatedLineItems = [...projectData.line_items];
    updatedLineItems[index] = itemWithAmount;
    
    setProjectData(prevData => ({
      ...prevData,
      line_items: updatedLineItems
    }));
  };

  const deleteLineItem = (index) => {
    const updatedLineItems = [...projectData.line_items];
    updatedLineItems.splice(index, 1);
    
    setProjectData(prevData => ({
      ...prevData,
      line_items: updatedLineItems
    }));
  };

  const updateSettings = (settings) => {
    setProjectData(prevData => ({
      ...prevData,
      settings: {
        ...prevData.settings,
        ...settings
      }
    }));
  };

  const projectManager = {
    getProjectData: () => projectData,
    getProjectInfo: () => projectData.project_info,
    setProjectInfo: updateProjectInfo,
    getRooms: () => projectData.rooms,
    addRoom,
    deleteRoom,
    getLineItems: (room) => room 
      ? projectData.line_items.filter(item => item.room === room)
      : projectData.line_items,
    addLineItem,
    updateLineItem,
    deleteLineItem,
    getSettings: () => projectData.settings,
    updateSettings,
  };

  const calculator = {
    calculateItemAmount,
    calculateRoomTotals,
    calculateSubtotal,
    calculateGST,
    calculateDiscount,
    calculateGrandTotal,
    getMaterialOptionsFromRateCard: (rateCardItem) => {
      const materialOptions = [];
      const priceAdditions = {};
      let baseMaterial = null;
      
      if (rateCardItem.material_options) {
        const optionsList = rateCardItem.material_options.split(',').map(opt => opt.trim());
        
        materialOptions.push(...optionsList);
        if (optionsList.length > 0) {
          baseMaterial = optionsList[0];
          priceAdditions[baseMaterial] = 0;  // Base material has no additional cost
          
          // Parse material prices from rate card if available
          const materialPrices = {};
          if (rateCardItem.material_prices) {
            const pairs = rateCardItem.material_prices.split(',');
            for (const pair of pairs) {
              if (pair.includes(':')) {
                const [name, priceStr] = pair.split(':', 2);
                const trimmedName = name.trim();
                const price = parseFloat(priceStr.trim());
                if (!isNaN(price)) {
                  materialPrices[trimmedName] = price;
                }
              }
            }
          }
          
          // Set prices for each material
          for (const option of optionsList.slice(1)) {  // Skip base material
            if (option in materialPrices) {
              priceAdditions[option] = materialPrices[option];
            } else {
              // Use default prices if not specified
              const optionLower = option.toLowerCase();
              if (optionLower === "laminate") {
                priceAdditions[option] = 0;
              } else if (optionLower === "veneer") {
                priceAdditions[option] = 500;
              } else if (optionLower === "pu") {
                priceAdditions[option] = 800;
              } else if (optionLower === "acrylic") {
                priceAdditions[option] = 600;
              } else if (optionLower === "premium") {
                priceAdditions[option] = 400;
              } else if (optionLower === "texture") {
                priceAdditions[option] = 200;
              } else {
                // Default addition of ₹300 per SFT
                priceAdditions[option] = 300;
              }
            }
          }
        }
      }
      
      return {
        options: materialOptions,
        base_material: baseMaterial,
        price_additions: priceAdditions
      };
    },
    getAddOnsFromRateCard: (rateCardItem) => {
      const addOns = {};
      
      if (rateCardItem.add_ons && rateCardItem.add_ons.toLowerCase() !== "none") {
        const addOnsList = rateCardItem.add_ons.split(',').map(addon => addon.trim());
        
        // Parse add-on prices from rate card if available
        const addonPrices = {};
        if (rateCardItem.addon_prices) {
          const pairs = rateCardItem.addon_prices.split(',');
          for (const pair of pairs) {
            if (pair.includes(':')) {
              const [name, priceStr] = pair.split(':', 2);
              const trimmedName = name.trim();
              const price = parseFloat(priceStr.trim());
              if (!isNaN(price)) {
                addonPrices[trimmedName] = price;
              }
            }
          }
        }
        
        // Create structured add-ons object
        for (const addOn of addOnsList) {
          let ratePerUnit = 0;
          let description = "";
          
          // Get price from rate card if available, otherwise use defaults
          if (addOn in addonPrices) {
            ratePerUnit = addonPrices[addOn];
            description = `${addOn} (₹${ratePerUnit} per unit)`;
          } else {
            // Set reasonable default rates for common add-ons
            if (addOn.toLowerCase() === "profile door") {
              ratePerUnit = 150;
              description = "Premium profile door finish";
            } else if (addOn.toLowerCase() === "lights") {
              ratePerUnit = 250;
              description = "LED strip lighting";
            } else {
              ratePerUnit = 100;  // Default rate
              description = `Additional ${addOn} feature`;
            }
          }
          
          // Add to add-ons dictionary
          addOns[addOn] = {
            selected: false,  // Default to not selected
            rate_per_unit: ratePerUnit,
            description: description
          };
        }
      }
      
      return addOns;
    }
  };

  const rateCardManager = {
    getItems: () => rateCardItems,
    getCategories: () => {
      const categories = new Set();
      rateCardItems.forEach(item => {
        if (item.category) {
          categories.add(item.category);
        }
      });
      return Array.from(categories).sort();
    },
    getItemsByCategory: (category) => {
      return rateCardItems.filter(item => item.category === category);
    },
    addItem: (item) => {
      setRateCardItems(prevItems => [...prevItems, item]);
    },
    updateItem: (index, item) => {
      const updatedItems = [...rateCardItems];
      updatedItems[index] = item;
      setRateCardItems(updatedItems);
    },
    deleteItem: (index) => {
      const updatedItems = [...rateCardItems];
      updatedItems.splice(index, 1);
      setRateCardItems(updatedItems);
    }
  };

  return (
    <div className="app">
      <header className="app-header" style={{ backgroundColor: CompanyConfig.HEADER_BG_COLOR }}>
        <div className="app-logo">
          {/* Replace with your logo or use placeholder */}
          <div style={{ width: 250, height: 100, backgroundColor: '#f5f5f5', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#333' }}>
            Home Project Logo
          </div>
        </div>
        <h1 style={{ color: CompanyConfig.HEADER_TEXT_COLOR }}>Interior Design Quote Tool</h1>
      </header>
      
      <main className="app-content">
        <Tabs>
          <Tab title="Project Info">
            <ProjectInfoTab projectManager={projectManager} />
          </Tab>
          <Tab title="Rooms">
            <RoomsTab projectManager={projectManager} />
          </Tab>
          <Tab title="Scope of Work">
            <ScopeOfWorkTab 
              projectManager={projectManager} 
              calculator={calculator} 
              rateCardManager={rateCardManager} 
            />
          </Tab>
          <Tab title="Dashboard">
            <DashboardTab 
              projectManager={projectManager} 
              calculator={calculator} 
            />
          </Tab>
          <Tab title="Export">
            <ExportTab 
              projectManager={projectManager} 
            />
          </Tab>
          <Tab title="Rate Card">
            <RateCardTab rateCardManager={rateCardManager} />
          </Tab>
        </Tabs>
      </main>
      
      <footer className="app-footer">
        <div className="status-bar">
          Ready - {CompanyConfig.COMPANY_NAME}
        </div>
      </footer>
    </div>
  );
};

export default App;