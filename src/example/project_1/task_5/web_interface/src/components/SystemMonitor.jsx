import React from "react";
import { Box, LinearProgress, Typography } from "@mui/material";

const ProgressBar = ({ value, label }) => (
  <Box
    display="flex"
    flexDirection="column"
    alignItems="center"
    sx={{ marginBottom: "40px" }} // Khoảng cách giữa các thanh
  >
    <LinearProgress
      variant="determinate"
      value={value}
      sx={{
        height: "20px",
        width: "200px",
        borderRadius: "5px",
        backgroundColor: "#e0e0e0",
        transform: "rotate(270deg)",
        "& .MuiLinearProgress-bar": {
          backgroundColor: "#a7c957",
        },
      }}
    />
    <Typography sx={{ marginTop: "100px", fontSize: "18px" }}>{label}</Typography>
  </Box>
);

const SystemMonitor = () => {
  return (
    <Box
      display="flex"
      alignItems="center"
      justifyContent="center"
      sx={{
        width: "100%",
        height: "100%", // Toàn màn hình
        padding: "20px",
        marginTop: "80px",
      }}
    >
      <ProgressBar value={70} label="Temperate" />
      <ProgressBar value={50} label="Memory" />
      <ProgressBar value={30} label="CPU" />
    </Box>
  );
};

export default SystemMonitor;
