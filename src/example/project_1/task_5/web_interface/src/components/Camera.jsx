import React, { useState } from 'react';
import { Box, Typography } from '@mui/material';
import { tokens } from "../theme";
import Alert from '@mui/material/Alert';

const Camera = () => {
  const [connected, setConnected] = useState(true);  // Mặc định là kết nối
  const [ros, setRos] = useState(null);
  const [imageError, setImageError] = useState(false);  // Kiểm tra có lỗi tải ảnh hay không

  // Hàm xử lý lỗi khi không thể tải được video stream
  const handleError = () => {
    setImageError(true);
  };

  return (
    <Box display="flex" justifyContent="center" alignItems="center" height="100%">
      {imageError ? (
        <Box display="flex" justifyContent="center" alignItems="center" height="290px" width="100%">
          <Alert variant='outlined' severity="error" sx={{ width: '260px', fontSize: '16px' }}>
          Cannot to get video stream!
          </Alert>
        </Box>
      ) : (
        <img
          id="my_image"
          src={`http://192.168.8.101:8080/stream?topic=/automobile/rcCar/camera_follow/image_raw&type=ros_compressed`}
          style={{
            height: '100%',
            width: '100%',
            objectFit: 'cover',
            borderRadius: "25px",
          }}
          alt="loading..."
          onError={handleError}  // Gọi handleError khi có lỗi
        />
      )}
    </Box>
  );
};

export default Camera;
