import React, { useState, useEffect } from 'react';

const DEFAULT_ROOM_TYPES = ["Bedroom", "Kitchen", "Living Room", "Bathroom", "Dining Room", "Study", "Balcony"];

const RoomsTab = ({ projectManager }) => {
  const [rooms, setRooms] = useState([]);
  const [selectedRoomType, setSelectedRoomType] = useState(DEFAULT_ROOM_TYPES[0]);
  const [statusMessage, setStatusMessage] = useState(null);

  // Load rooms when component mounts
  useEffect(() => {
    const projectRooms = projectManager.getRooms();
    setRooms(projectRooms);
  }, [projectManager]);

  const handleAddRoom = () => {
    const roomCount = rooms.length + 1;
    const roomName = `${selectedRoomType} ${roomCount}`;
    
    const newRoom = {
      type: selectedRoomType,
      name: roomName
    };
    
    projectManager.addRoom(newRoom);
    
    // Update local state
    setRooms([...rooms, newRoom]);
    
    setStatusMessage({ type: 'success', text: `Added ${roomName}` });
    setTimeout(() => setStatusMessage(null), 2000);
  };

  const handleDeleteRoom = (index) => {
    const roomToDelete = rooms[index];
    
    if (window.confirm(`Are you sure you want to delete '${roomToDelete.name}'?`)) {
      projectManager.deleteRoom(index);
      
      // Update local state
      const updatedRooms = [...rooms];
      updatedRooms.splice(index, 1);
      setRooms(updatedRooms);
      
      setStatusMessage({ type: 'success', text: `Deleted ${roomToDelete.name}` });
      setTimeout(() => setStatusMessage(null), 2000);
    }
  };

  const handleSaveTemplate = () => {
    // This would save the current rooms as a template for future projects
    setStatusMessage({ type: 'info', text: `Room template feature will be added in future version` });
    setTimeout(() => setStatusMessage(null), 3000);
  };
  
  return (
    <div className="rooms-tab">
      <div className="controls mb-2">
        <div className="room-controls">
          <label htmlFor="room-type">Room Type:</label>
          <select 
            id="room-type"
            value={selectedRoomType}
            onChange={(e) => setSelectedRoomType(e.target.value)}
          >
            {DEFAULT_ROOM_TYPES.map((type) => (
              <option key={type} value={type}>{type}</option>
            ))}
          </select>
          
          <button onClick={handleAddRoom}>Add Room</button>
          <button onClick={handleSaveTemplate}>Save as Template</button>
        </div>
      </div>
      
      <div className="rooms-table-container">
        <table className="rooms-table">
          <thead>
            <tr>
              <th>Room Type</th>
              <th>Room Name</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {rooms.length === 0 ? (
              <tr>
                <td colSpan="3" className="text-center">No rooms added yet</td>
              </tr>
            ) : (
              rooms.map((room, index) => (
                <tr key={index}>
                  <td>{room.type}</td>
                  <td>{room.name}</td>
                  <td>
                    <button onClick={() => handleDeleteRoom(index)}>Delete</button>
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
    </div>
  );
};

export default RoomsTab;