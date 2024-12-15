import { Canvas } from "@react-three/fiber";
import { useGLTF, Stage, PresentationControls } from "@react-three/drei";
import { LinearProgress } from "@mui/material";
import EvStationIcon from '@mui/icons-material/EvStation';
import React, { useState, useEffect } from 'react';
import { tokens } from "../theme";
import { Box, Typography, useTheme } from "@mui/material";
import ROSLIB from "roslib";

const InfoItem = ({ value, label }) => (
    <Typography variant="h3" fontSize="20px" textAlign="center" fontWeight="bold">
        {value} <span style={{ display: "block", fontSize: "14px", marginTop: "10px", fontWeight: "normal" }}>{label}</span>
    </Typography>
);




const Information = () => {
    const [ros, setRos] = useState(null);
    const theme = useTheme();
    const colors = tokens(theme.palette.mode);
    const [progress] = useState(50);
    const [vel, setVel] = useState(0);

    // States to handle N, D, P, R signals
    const [signals, setSignals] = useState({
        Stop: false,
        Manual: true,
        Legacy: false,
        Auto: false
    });

    const initConnection = () => {
        const rosInstance = new ROSLIB.Ros();
        setRos(rosInstance);
    
        rosInstance.on("connection", () => {
            console.log("Connection established in Specification");
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
            console.log("Connection error at Specification!");
        }
    };

    useEffect(() => {
        initConnection();
    }, []);  
    useEffect(() => {
        if (ros) {
            getVelocity();
        }
    }, [ros]);  
    const getVelocity = () => {
        const velocitySubscriber = new ROSLIB.Topic({
            ros: ros,
            name: "/automobile/command",
            messageType: "std_msgs/String",
        });
    
        velocitySubscriber.subscribe((message) => {
            try {
                // Parse the string to an object
                const messageData = JSON.parse(message.data);
                const speed = messageData.speed * 10;
    
                // Extract the decimal part to 2 places
                const speedWithDecimal = speed.toFixed(2); // 2 decimal places
                setVel(speedWithDecimal);
            } catch (error) {
                console.error("Error parsing message data: ", error);
            }
        });
    };
    


    return (
        <Box display="flex" flexDirection="column" justifyContent="center" alignItems="center">
            {/* 3D Model */}
            <div style={{ width: "400px", height: "400px", marginTop: "-80px" }}>
                <Canvas style={{ width: "100%", height: "100%", backgroundColor: "transparent" }} shadows camera={{ fov: 45 }}>
                    <PresentationControls speed={1.5} global zoom={0.5} polar={[-0.1, Math.PI / 4]}>
                        <Stage environment="sunset">
                            <Model scale={[0.01, 0.01, 0.01]} />
                        </Stage>
                    </PresentationControls>
                </Canvas>
            </div>

            {/* Title */}
            <Typography variant="h3" marginTop="-90px">BMW 320i Sportline</Typography>

            {/* Linear Progress */}
            <LinearProgress
                variant="determinate"
                value={progress}
                sx={{
                    height: 20,
                    width: 430,
                    borderRadius: "20px",
                    marginTop: "40px",
                    "& .MuiLinearProgress-bar": {
                        backgroundColor: "#38b000",
                    }
                }}
            />

            {/* Info Section */}
            <Box marginTop="20px" display="flex" alignItems="center" justifyContent="space-evenly" width="100%">
                <EvStationIcon sx={{ color: "#5fa8d3", fontSize: "40px" }} />
                <InfoItem value="36.646 Km" label="Remaining" />
                <InfoItem value="128 wh/km" label="Average" />
                <InfoItem value="36.6 kWm" label="full capacity" />
            </Box>

            {/* Signal Box Section */}


            <Box
                backgroundColor={colors.primary[600]}
                sx={{
                    borderRadius: "0 20px 20px 0",   // Chỉ làm tròn hai góc bên phải
                    marginTop: "80px",
                    marginLeft: "-280px",
                    width: "250px",
                    height: "200px",
                    border: "2px solid #5fa8d3",
                    borderLeft: "none",
                    display: "flex",
                    flexDirection: "column",
                    justifyContent: "center",
                    alignItems: "center",
                    textAlign: "center",
                }}
            >
                <Typography sx={{ fontSize: "25px", fontWeight: "600" }}>Speed</Typography>
                <Typography sx={{ fontSize: "60px", fontWeight: "600" }}>{vel}</Typography>
                <Typography sx={{ fontSize: "23px", }}>m/s</Typography>
            </Box>

            <Box marginTop="100px" backgroundColor={colors.primary[600]} display="flex" borderRadius="10px" justifyContent="space-evenly" width="80%">
                {["Stop", "Manual", "Legacy", "Auto"].map((signal) => (
                    <Box
                        key={signal}
                        sx={{
                            backgroundColor: signals[signal] ? "#5fa8d3" : "transparent", // Green if true, grey if false
                            color: "#fff",
                            borderRadius: "10px",
                            width: "25%",
                            height: "50px",
                            display: "flex",
                            justifyContent: "center",
                            alignItems: "center",
                            fontSize: "20px",
                            fontWeight: "bold",
                        }}
                    >
                        {signal}
                    </Box>
                ))}
            </Box>
        </Box>
    );
};

const Model = (props) => {
    const { scene } = useGLTF("/bmw_obeject.glb");
    return <primitive object={scene} {...props} />;
};

export default Information;
