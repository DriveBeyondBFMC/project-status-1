import { Box, Button, IconButton, Typography, useTheme } from "@mui/material";
import { tokens } from "../../theme";
import { mockTransactions } from "../../data/mockData";

import Information from "../../components/Information";
import Map from "../../components/Map";
import Camera from "../../components/Camera";
import SystemMonitor from "../../components/SystemMonitor"
const Dashboard = () => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);

  return (
    <Box m="20px">
      <Box
        display="grid"
        gridTemplateColumns="repeat(16, 2fr)"
        gridAutoRows="20px"
        gap="10px"
      >

        {/* Velocity */}
        <Box
          gridColumn="span 4"
          gridRow="span 32"
          backgroundColor={colors.primary[400]}
          sx={{ borderRadius: "30px", marginBottom: "100px" }}
          width="530px"
        >
          <Information></Information>
        </Box>

        {/* Map */}
        <Box
          gridColumn="span 12"
          gridRow="span 19"
          backgroundColor={colors.primary[400]}
          sx={{ marginLeft: "30px", marginRight: "0px", borderRadius: "30px" }}
        >
          <Map>

          </Map>
        </Box>
        {/* Specification */}
        <Box
          gridColumn="span 5"
          gridRow="span 10"
          backgroundColor={colors.primary[400]}
          sx={{
            marginTop: "10px",
            marginLeft: "30px",
            border: "5px solid #ffffff", // Fix màu trắng (thêm một 'f')
            borderRadius: "30px", // Đúng đơn vị px
          }}
        >
          <Camera></Camera>
        </Box>

        <Box
          gridColumn="span 7"
          gridRow="span 10"
          backgroundColor={colors.primary[400]}
          sx={{
            borderRadius: "30px", // Đúng đơn vị px
            marginLeft: "0px",
            marginTop: "10px",
          }}
        >
          <SystemMonitor></SystemMonitor>
        </Box>
      </Box>
    </Box>
  );
};

export default Dashboard;
