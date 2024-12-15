import React, { useState, useEffect } from 'react';
import ROSLIB from "roslib";
import AddIcon from '@mui/icons-material/Add';
import RemoveIcon from '@mui/icons-material/Remove';
import MyLocationIcon from '@mui/icons-material/MyLocation';
class KalmanFilter {
  constructor(processNoise, measurementNoise, estimatedError) {
    this.processNoise = processNoise;
    this.measurementNoise = measurementNoise;
    this.estimatedError = estimatedError;
    this.lastEstimate = 0;
    this.lastKalmanGain = 0;
  }

  filter(measurement) {
    const prediction = this.lastEstimate;
    const kalmanGain = this.estimatedError / (this.estimatedError + this.measurementNoise);
    const currentEstimate = prediction + kalmanGain * (measurement - prediction);
    this.estimatedError = (1 - kalmanGain) * (this.estimatedError + this.processNoise);
    this.lastEstimate = currentEstimate;
    this.lastKalmanGain = kalmanGain;
    return currentEstimate;
  }
}
function Map() {
  const [scale, setScale] = useState(1); // Trạng thái cho zoom
  const [position, setPosition] = useState({ x: 0, y: 0 }); // Trạng thái cho di chuyển
  const [dragging, setDragging] = useState(false); // Trạng thái kéo
  const [startPosition, setStartPosition] = useState({ x: 0, y: 0 }); // Lưu vị trí chuột bắt đầu
  const [markerA, setMarkerA] = useState(55); // Tọa độ pixel của dấu chấm trên ảnh gốc
  const [markerB, setMarkerB] = useState(55);
  const [x, setX] = useState(0);
  const [y, setY] = useState(0);
  const [ros, setRos] = useState(null);
  const kalmanA = new KalmanFilter(0.1, 1, 1);
  const kalmanB = new KalmanFilter(0.1, 1, 1);
  const initConnection = () => {
    const rosInstance = new ROSLIB.Ros();
    setRos(rosInstance);

    rosInstance.on("connection", () => {
      console.log("Connection established in map");
    });

    rosInstance.on("close", () => {
      setTimeout(() => {
        try {
          rosInstance.connect("ws://192.168.8.101:9090");
        } catch (error) {
          console.log("Connection problem!");
        }
      }, 3000);
    });

    try {
      rosInstance.connect("ws://192.168.8.101:9090");
    } catch (error) {
      console.log("Connection error at Map!");
    }
  };
  useEffect(() => {
    initConnection();
  }, []);
  useEffect(() => {
    if (ros) {
      getRobotState();
    }
  }, [ros]);

  const getRobotState = () => {
    const poseSubscriber = new ROSLIB.Topic({
      ros: ros,
      name: "/automobile/localisation",
      messageType: "utils/localisation",
    });

    poseSubscriber.subscribe((message) => {
      const filteredMarkerA = kalmanA.filter(message.posA * (979 / 15));
      const filteredMarkerB = kalmanB.filter((message.posB - 0.3) * (1021 / 15));
      setMarkerA(filteredMarkerA);
      setMarkerB(filteredMarkerB);
    });
  }

  useEffect(() => {
    setPosition({ x: markerA, y: markerB });
    setStartPosition({ x: markerA, y: markerB });
  }, [markerA, markerB]);

  const handleZoom = (delta) => {
    setScale((prev) => Math.min(Math.max(prev + delta, 0.5), 3)); // Giới hạn zoom từ 0.5x đến 3x
  };

  const handleMouseDown = (e) => {
    setDragging(true);
    setStartPosition({ x: e.clientX - position.x, y: e.clientY - position.y });
  };

  // Khi nhả chuột
  const handleMouseUp = () => {
    setDragging(false);
  };

  // Xử lý kéo ảnh khi di chuyển chuột
  const handleMouseMove = (e) => {
    if (dragging) {
      const x = e.clientX - startPosition.x;
      const y = e.clientY - startPosition.y;
      setPosition({ x, y });
    }
  };

  useEffect(() => {
    const centerViewport = { x: 530 / 2, y: 530 / 2 }; // Tâm của viewport (530px x 530px)
    setPosition({
      x: centerViewport.x - markerA * scale,
      y: centerViewport.y - markerB * scale,
    });
  }, [markerA, markerB, scale]);

  return (
    <div
      style={{
        width: '100%',
        height: '100%',
        overflow: 'hidden',
        position: 'relative',
        background: 'black',
        borderRadius: '30px',
      }}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp} // Khi chuột rời khỏi khu vực
    >
      <img
        src={`${process.env.PUBLIC_URL}/assets/Track2025_2.jpg`}
        alt="Track"
        style={{
          transform: `translate(${position.x}px, ${position.y}px) scale(${scale})`,
          transformOrigin: 'top left', // Điểm gốc là góc trái trên ảnh
          width: '1000px',
          height: '1021px',
          objectFit: 'cover',
          cursor: dragging ? 'grabbing' : 'grab',
          transition: 'transform 0.3s ease-out', // Mượt mà khi thay đổi vị trí và zoom
        }}
        onMouseDown={handleMouseDown}
        draggable={false} // Vô hiệu hóa drag mặc định của ảnh
      />
      {/* Hiển thị dấu chấm đỏ */}
      <MyLocationIcon
        style={{
          position: 'absolute',
          top: `${(markerB * scale) + position.y}px`, // Áp dụng zoom và dịch chuyển
          left: `${(markerA * scale) + position.x}px`, // Áp dụng zoom và dịch chuyển
          width: '25px',
          height: '25px',
          color: "#4cc9f0",
          borderRadius: '50%',
          pointerEvents: 'none', // Vô hiệu hóa tương tác với dấu chấm
          transition: 'top 20.5s ease-out, left 20.5s ease-out', // Mượt mà khi thay đổi vị trí của dấu chấm
        }}
      ></MyLocationIcon>
      <div
        style={{
          position: 'absolute',
          top: '20px',
          right: '20px',
          display: 'flex',
          justifyContent: 'center', // Center the buttons horizontally
          alignItems: 'center', // Center the buttons vertically
          gap: '5px',
          width: "100px",
          height: "50px",
          backgroundColor: "gray",
          borderRadius: '10px', // Rounded corners for the background
          padding: '5px', // Optional: space around buttons
        }}
      >
        <button
          onClick={() => handleZoom(0.1)}
          style={{
            padding: '5px 10px',
            border: 'none',
            color: 'white',
            cursor: 'pointer',
            background:"#495057",
            borderRadius: '5px'
          }}
        >
          <AddIcon></AddIcon>
        </button>
        <button
          onClick={() => handleZoom(-0.1)}
          style={{
            padding: '5px 10px',
            border: 'none',
            color: 'white',
            background:"#495057",
            cursor: 'pointer',
            borderRadius: '5px'
          }}
        >
          <RemoveIcon></RemoveIcon>
        </button>
      </div>

    </div>
  );
}

export default Map;
