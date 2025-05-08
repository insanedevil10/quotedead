import React, { useState, useEffect } from 'react';
import ItemOptionsDialog from './dialogs/ItemOptionsDialog';
import SelectFromRateCardDialog from './dialogs/SelectFromRateCardDialog';

const ScopeOfWorkTab = ({ projectManager, calculator, rateCardManager }) => {
  const [rooms, setRooms] = useState([]);
  const [selectedRoom, setSelectedRoom] = useState('');
  const [lineItems, setLineItems] = useState([]);
  const [showItemDialog, setShowItemDialog] = useState(false);
  const [showRateCardDialog, setShowRateCardDialog] = useState(false);
  const [currentItem, setCurrentItem] = useState(null);
  const [currentItemIndex, setCurrentItemIndex] = useState(-1);
  const [statusMessage, setStatusMessage] = useState(null);

  // Load rooms when component mounts or changes
  useEffect(() => {
    const projectRooms = projectManager.getRooms();
    setRooms(projectRooms);
    
    // Select the first room if available and none selected
    if (projectRooms.length > 0 && !selectedRoom) {
      setSelectedRoom(projectRooms[0].name);
    }
  }, [projectManager, selectedRoom]);

  // Load line items when selected room changes
  useEffect(() => {
    if (selectedRoom) {
      const items = projectManager.getLineItems(selectedRoom);
      setLineItems(items);
    } else {
      setLineItems([]);
    }
  }, [projectManager, selectedRoom]);

  const handleRoomChange = (e) => {
    setSelectedRoom(e.target.value);
  };

  const handleAddLineItem = () => {
    if (!selectedRoom) {
      setStatusMessage({ type: 'error', text: 'Please select a room first' });
      setTimeout(() => setStatusMessage(null), 3000);
      return;
    }

    // Create a new empty item
    const newItem = {
      room: selectedRoom,
      item: "New Item",
      uom: "SFT",
      length: 0,
      height: 0,
      quantity: 1,
      rate: 0,
      amount: 0
    };

    setCurrentItem(newItem);
    setCurrentItemIndex(-1); // -1 indicates a new item
    setShowItemDialog(true);
  };

  const handleEditItem = (index) => {
    const item = { ...lineItems[index] };
    setCurrentItem(item);
    setCurrentItemIndex(index);
    setShowItemDialog(true);
  };

  const handleDeleteItem = (index) => {
    const itemToDelete = lineItems[index];
    
    if (window.confirm(`Are you sure you want to delete '${itemToDelete.item}'?`)) {
      // Find the actual index in the full list
      const allItems = projectManager.getLineItems();
      let actualIndex = -1;
      
      for (let i = 0; i < allItems.length; i++) {
        if (allItems[i].room === selectedRoom && allItems[i].item === itemToDelete.item) {
          actualIndex = i;
          break;
        }
      }
      
      if (actualIndex !== -1) {
        projectManager.deleteLineItem(actualIndex);
        
        // Update local state
        const updatedItems = [...lineItems];
        updatedItems.splice(index, 1);
        setLineItems(updatedItems);
        
        setStatusMessage({ type: 'success', text: `Deleted ${itemToDelete.item}` });
        setTimeout(() => setStatusMessage(null), 2000);
      }
    }
  };

  const handleDuplicateItem = (index) => {
    const itemToDuplicate = { ...lineItems[index] };
    itemToDuplicate.item = `${itemToDuplicate.item} (Copy)`;
    
    projectManager.addLineItem(itemToDuplicate);
    
    // Update local state
    setLineItems([...lineItems, itemToDuplicate]);
    
    setStatusMessage({ type: 'success', text: `Duplicated item` });
    setTimeout(() => setStatusMessage(null), 2000);
  };

  const handleItemDialogSave = (item) => {
    // Calculate amount
    const updatedItem = {
      ...item,
      amount: calculator.calculateItemAmount(item)
    };
    
    if (currentItemIndex === -1) {
      // Add new item
      projectManager.addLineItem(updatedItem);
      setLineItems([...lineItems, updatedItem]);
    } else {
      // Update existing item
      // Find the actual index in the full list
      const allItems = projectManager.getLineItems();
      let actualIndex = -1;
      
      for (let i = 0; i < allItems.length; i++) {
        if (allItems[i].room === selectedRoom && i === currentItemIndex) {
          actualIndex = i;
          break;
        }
      }
      
      if (actualIndex !== -1) {
        projectManager.updateLineItem(actualIndex, updatedItem);
        
        // Update local state
        const updatedItems = [...lineItems];
        updatedItems[currentItemIndex] = updatedItem;
        setLineItems(updatedItems);
      }
    }
    
    setShowItemDialog(false);
    setStatusMessage({ type: 'success', text: `${currentItemIndex === -1 ? 'Added' : 'Updated'} item` });
    setTimeout(() => setStatusMessage(null), 2000);
  };

  const handleItemDialogCancel = () => {
    setShowItemDialog(false);
  };

  const handleAddFromRateCard = () => {
    if (!selectedRoom) {
      setStatusMessage({ type: 'error', text: 'Please select a room first' });
      setTimeout(() => setStatusMessage(null), 3000);
      return;
    }
    
    setShowRateCardDialog(true);
  };

  const handleRateCardDialogSave = (selectedItems) => {
    // Add all selected items to the current room
    const newItems = selectedItems.map(item => ({
      ...item,
      room: selectedRoom
    }));
    
    newItems.forEach(item => {
      projectManager.addLineItem(item);
    });
    
    // Update local state
    setLineItems([...lineItems, ...newItems]);
    
    setShowRateCardDialog(false);
    setStatusMessage({ type: 'success', text: `Added ${newItems.length} items from rate card` });
    setTimeout(() => setStatusMessage(null), 2000);
  };

  const handleRateCardDialogCancel = () => {
    setShowRateCardDialog(false);
  };

  return (
    <div className="scope-of-work-tab">
      <div className="toolbar mb-2">
        <button onClick={handleAddLineItem}>Add Item</button>
        <button onClick={handleAddFromRateCard}>From Rate Card</button>
        <button disabled={lineItems.length === 0}>Bulk Edit</button>
      </div>
      
      <div className="room-selector mb-2">
        <label htmlFor="room-select">Select Room:</label>
        <select 
          id="room-select"
          value={selectedRoom}
          onChange={handleRoomChange}
        >
          <option value="">Select a room</option>
          {rooms.map((room, index) => (
            <option key={index} value={room.name}>{room.name}</option>
          ))}
        </select>
      </div>
      
      <div className="line-items-table-container">
        <table className="line-items-table">
          <thead>
            <tr>
              <th>Item</th>
              <th>UOM</th>
              <th>Length</th>
              <th>Height</th>
              <th>Quantity</th>
              <th>Material</th>
              <th>Rate (₹)</th>
              <th>Amount (₹)</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {lineItems.length === 0 ? (
              <tr>
                <td colSpan="9" className="text-center">
                  {selectedRoom 
                    ? 'No items added to this room yet' 
                    : 'Please select a room first'}
                </td>
              </tr>
            ) : (
              lineItems.map((item, index) => (
                <tr key={index}>
                  <td>{item.item}</td>
                  <td>{item.uom}</td>
                  <td>{item.length}</td>
                  <td>{item.height}</td>
                  <td>{item.quantity}</td>
                  <td>{item.material?.selected || ''}</td>
                  <td>{item.rate}</td>
                  <td>₹{item.amount.toFixed(2)}</td>
                  <td>
                    <div className="button-group">
                      <button onClick={() => handleEditItem(index)}>Edit</button>
                      <button onClick={() => handleDuplicateItem(index)}>Duplicate</button>
                      <button onClick={() => handleDeleteItem(index)}>Delete</button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
      
      {statusMessage && (
        <div className={`status-message status-${statusMessage.type} mt-2`}>
          {statusMessage.text}
        </div>
      )}
      
      {showItemDialog && (
        <ItemOptionsDialog
          item={currentItem}
          calculator={calculator}
          onSave={handleItemDialogSave}
          onCancel={handleItemDialogCancel}
        />
      )}
      
      {showRateCardDialog && (
        <SelectFromRateCardDialog
          rateCardManager={rateCardManager}
          calculator={calculator}
          onSave={handleRateCardDialogSave}
          onCancel={handleRateCardDialogCancel}
        />
      )}
    </div>
  );
};

export default ScopeOfWorkTab;