import React, { useState, useEffect } from 'react';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const COLORS = ['#C62828', '#AD1457', '#6A1B9A', '#4527A0', '#283593', '#1565C0', '#0277BD', '#00838F', '#00695C', '#2E7D32', '#558B2F', '#9E9D24'];

const DashboardTab = ({ projectManager, calculator }) => {
  const [rooms, setRooms] = useState([]);
  const [lineItems, setLineItems] = useState([]);
  const [roomTotals, setRoomTotals] = useState({});
  const [itemCategoryTotals, setItemCategoryTotals] = useState([]);
  const [showPercentages, setShowPercentages] = useState(true);
  const [sortType, setSortType] = useState('value-desc');
  const [gstPercent, setGstPercent] = useState(18);
  const [discountPercent, setDiscountPercent] = useState(0);
  const [totals, setTotals] = useState({
    subtotal: 0,
    gst: 0,
    discount: 0,
    grandTotal: 0
  });
  const [stats, setStats] = useState({
    totalRooms: 0,
    totalItems: 0,
    avgRoomCost: 0,
    avgItemCost: 0,
    highestCostRoom: 'None',
    highestCostItem: 'None'
  });

  // Load rooms and line items when component mounts or changes
  useEffect(() => {
    const projectRooms = projectManager.getRooms();
    const projectItems = projectManager.getLineItems();
    
    setRooms(projectRooms);
    setLineItems(projectItems);
    
    // Load settings
    const settings = projectManager.getSettings();
    setGstPercent(settings.gst);
    setDiscountPercent(settings.discount);
  }, [projectManager]);

  // Calculate totals when line items or settings change
  useEffect(() => {
    if (!calculator) return;
    
    // Calculate room totals
    const roomTotalsData = calculator.calculateRoomTotals(lineItems);
    setRoomTotals(roomTotalsData);
    
    // Calculate UOM category totals
    const uomCategories = {};
    for (const item of lineItems) {
      const uom = item.uom || 'Unknown';
      if (!uomCategories[uom]) {
        uomCategories[uom] = 0;
      }
      uomCategories[uom] += item.amount || 0;
    }
    
    // Convert to array for charts
    const uomCategoriesArray = Object.entries(uomCategories).map(([name, value]) => ({
      name,
      value
    }));
    
    // Apply sorting
    if (sortType === 'value-desc') {
      uomCategoriesArray.sort((a, b) => b.value - a.value);
    } else if (sortType === 'value-asc') {
      uomCategoriesArray.sort((a, b) => a.value - b.value);
    } else if (sortType === 'name') {
      uomCategoriesArray.sort((a, b) => a.name.localeCompare(b.name));
    }
    
    setItemCategoryTotals(uomCategoriesArray);
    
    // Calculate financial totals
    const subtotal = calculator.calculateSubtotal(roomTotalsData);
    const gstAmount = calculator.calculateGST(subtotal, gstPercent);
    const discountAmount = calculator.calculateDiscount(subtotal, discountPercent);
    const grandTotal = calculator.calculateGrandTotal(subtotal, gstAmount, discountAmount);
    
    setTotals({
      subtotal,
      gst: gstAmount,
      discount: discountAmount,
      grandTotal
    });
    
    // Calculate statistics
    const statsData = {
      totalRooms: Object.keys(roomTotalsData).length,
      totalItems: lineItems.length,
      avgRoomCost: Object.keys(roomTotalsData).length > 0 
        ? subtotal / Object.keys(roomTotalsData).length
        : 0,
      avgItemCost: lineItems.length > 0 
        ? subtotal / lineItems.length
        : 0,
      highestCostRoom: 'None',
      highestCostItem: 'None'
    };
    
    // Find highest cost room
    if (Object.keys(roomTotalsData).length > 0) {
      const highestRoom = Object.entries(roomTotalsData)
        .reduce((max, [room, amount]) => 
          amount > max[1] ? [room, amount] : max, 
          ['', 0]
        );
      
      if (highestRoom[0]) {
        statsData.highestCostRoom = `${highestRoom[0]} (₹${highestRoom[1].toFixed(2)})`;
      }
    }
    
    // Find highest cost item
    if (lineItems.length > 0) {
      const highestItem = lineItems.reduce((max, item) => 
        (item.amount || 0) > (max.amount || 0) ? item : max, 
        { amount: 0 }
      );
      
      if (highestItem && highestItem.item) {
        statsData.highestCostItem = `${highestItem.item} in ${highestItem.room} (₹${(highestItem.amount || 0).toFixed(2)})`;
      }
    }
    
    setStats(statsData);
    
  }, [lineItems, calculator, gstPercent, discountPercent, sortType]);

  // Update settings when GST or discount changes
  useEffect(() => {
    projectManager.updateSettings({
      gst: gstPercent,
      discount: discountPercent
    });
  }, [projectManager, gstPercent, discountPercent]);

  const handleGstChange = (e) => {
    const value = parseInt(e.target.value, 10);
    if (!isNaN(value) && value >= 0 && value <= 100) {
      setGstPercent(value);
    }
  };

  const handleDiscountChange = (e) => {
    const value = parseInt(e.target.value, 10);
    if (!isNaN(value) && value >= 0 && value <= 100) {
      setDiscountPercent(value);
    }
  };

  const handleSortTypeChange = (e) => {
    setSortType(e.target.value);
  };

  const handleShowPercentagesChange = (e) => {
    setShowPercentages(e.target.checked);
  };

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="custom-tooltip">
          <p className="label">{`${data.name}`}</p>
          <p className="value">{`₹${data.value.toFixed(2)}`}</p>
          {showPercentages && totals.subtotal > 0 && (
            <p className="percent">{`${((data.value / totals.subtotal) * 100).toFixed(1)}%`}</p>
          )}
        </div>
      );
    }
    return null;
  };

  // Helper for PieChart label format
  const renderCustomizedLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent, index, name, value }) => {
    const RADIAN = Math.PI / 180;
    const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
    const x = cx + radius * Math.cos(-midAngle * RADIAN);
    const y = cy + radius * Math.sin(-midAngle * RADIAN);

    if (!showPercentages) {
      return `${name}: ₹${value.toFixed(0)}`;
    }
    
    return `${name}: ₹${value.toFixed(0)} (${(percent * 100).toFixed(1)}%)`;
  };

  return (
    <div className="dashboard-tab">
      <div className="dashboard-header">
        <h2>Project Dashboard</h2>
      </div>
      
      <div className="dashboard-charts">
        <div className="card">
          <h3 className="card-header">Room Cost Distribution</h3>
          <div className="chart-container" style={{ height: '300px' }}>
            {Object.keys(roomTotals).length === 0 ? (
              <div className="no-data">No data available. Add rooms and items to see charts.</div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={Object.entries(roomTotals).map(([name, value], index) => ({
                      name,
                      value,
                      color: COLORS[index % COLORS.length]
                    }))}
                    cx="50%"
                    cy="50%"
                    labelLine={true}
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="value"
                    nameKey="name"
                    label={renderCustomizedLabel}
                  >
                    {
                      Object.entries(roomTotals).map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))
                    }
                  </Pie>
                  <Tooltip content={<CustomTooltip />} />
                </PieChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>
        
        <div className="card">
          <h3 className="card-header">Item Category Breakdown</h3>
          <div className="chart-container" style={{ height: '300px' }}>
            {itemCategoryTotals.length === 0 ? (
              <div className="no-data">No data available. Add items to see charts.</div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={itemCategoryTotals}
                  margin={{ top: 10, right: 30, left: 20, bottom: 30 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis label={{ value: 'Amount (₹)', angle: -90, position: 'insideLeft' }} />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar dataKey="value" name="Amount (₹)">
                    {
                      itemCategoryTotals.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))
                    }
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>
      </div>
      
      <div className="dashboard-bottom">
        <div className="card summary-panel">
          <h3 className="card-header">Quote Summary</h3>
          
          <div className="summary-content">
            <div className="room-tree">
              <h4>Room-wise Costs</h4>
              <div className="room-list">
                {Object.keys(roomTotals).length === 0 ? (
                  <p>No rooms added yet</p>
                ) : (
                  <ul className="tree-view">
                    {Object.entries(roomTotals).map(([room, total], index) => (
                      <li key={index} className="tree-item">
                        <span className="tree-item-header">{room} - ₹{total.toFixed(2)}</span>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </div>
            
            <div className="totals-section">
              <div className="totals-row">
                <label>Subtotal:</label>
                <span className="amount">₹{totals.subtotal.toFixed(2)}</span>
              </div>
              
              <div className="totals-row">
                <label>
                  GST (%):
                  <input
                    type="number"
                    min="0"
                    max="100"
                    value={gstPercent}
                    onChange={handleGstChange}
                  />
                </label>
                <span className="amount">₹{totals.gst.toFixed(2)}</span>
              </div>
              
              <div className="totals-row">
                <label>
                  Discount (%):
                  <input
                    type="number"
                    min="0"
                    max="100"
                    value={discountPercent}
                    onChange={handleDiscountChange}
                  />
                </label>
                <span className="amount">₹{totals.discount.toFixed(2)}</span>
              </div>
              
              <div className="totals-row grand-total">
                <label>Grand Total:</label>
                <span className="amount">₹{totals.grandTotal.toFixed(2)}</span>
              </div>
            </div>
          </div>
        </div>
        
        <div className="card stats-panel">
          <h3 className="card-header">Project Statistics</h3>
          
          <div className="stats-content">
            <div className="stats-row">
              <label>Total Rooms:</label>
              <span>{stats.totalRooms}</span>
            </div>
            
            <div className="stats-row">
              <label>Total Line Items:</label>
              <span>{stats.totalItems}</span>
            </div>
            
            <div className="stats-row">
              <label>Average Room Cost:</label>
              <span>₹{stats.avgRoomCost.toFixed(2)}</span>
            </div>
            
            <div className="stats-row">
              <label>Average Item Cost:</label>
              <span>₹{stats.avgItemCost.toFixed(2)}</span>
            </div>
            
            <div className="stats-row">
              <label>Highest Cost Room:</label>
              <span>{stats.highestCostRoom}</span>
            </div>
            
            <div className="stats-row">
              <label>Highest Cost Item:</label>
              <span>{stats.highestCostItem}</span>
            </div>
          </div>
        </div>
      </div>
      
      <div className="chart-options">
        <div className="option-row">
          <label>
            <input
              type="checkbox"
              checked={showPercentages}
              onChange={handleShowPercentagesChange}
            />
            Show Percentages
          </label>
          
          <div className="sort-options">
            <label>Sort By:</label>
            <select value={sortType} onChange={handleSortTypeChange}>
              <option value="value-desc">Value (Descending)</option>
              <option value="value-asc">Value (Ascending)</option>
              <option value="name">Name</option>
            </select>
          </div>
          
          <button onClick={() => {
            // This would refresh the dashboard in a real app
            setRooms([...projectManager.getRooms()]);
            setLineItems([...projectManager.getLineItems()]);
          }}>Refresh Dashboard</button>
        </div>
      </div>
    </div>
  );
};

export default DashboardTab;