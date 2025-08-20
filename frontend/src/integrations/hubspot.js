import { useState, useEffect } from 'react';
import {
    Box,
    Button,
    CircularProgress,
    Autocomplete, 
    TextField,   
} from '@mui/material';
import axios from 'axios';
import { DataForm } from '../data-form'; 

export const HubspotIntegration = ({ user, org, integrationParams, setIntegrationParams }) => {
    const [isConnected, setIsConnected] = useState(false);
    const [isConnecting, setIsConnecting] = useState(false);
    const [selectedEntityType, setSelectedEntityType] = useState(null); 

    const entityTypeOptions = ['companies', 'contacts', 'all'];

    const handleConnectClick = async () => {
        try {
            setIsConnecting(true);
            const formData = new FormData();
            formData.append('user_id', user);
            formData.append('org_id', org);
            const response = await axios.post(`http://localhost:8000/integrations/hubspot/authorize`, formData);
            const authURL = response?.data;

            const newWindow = window.open(authURL, 'Hubspot Authorization', 'width=600, height=600');

            const pollTimer = window.setInterval(() => {
                if (newWindow?.closed !== false) { 
                    window.clearInterval(pollTimer);
                    handleWindowClosed();
                }
            }, 200);
        } catch (e) {
            setIsConnecting(false);
            alert(e?.response?.data?.detail);
        }
    }

    const handleWindowClosed = async () => {
        try {
            const formData = new FormData();
            formData.append('user_id', user);
            formData.append('org_id', org);
            const response = await axios.post(`http://localhost:8000/integrations/hubspot/credentials`, formData);
            const credentials = response.data;
            if (credentials) {
                setIsConnected(true);
                setIntegrationParams(prev => ({ ...prev, credentials: credentials, type: 'Hubspot' }));
            }
            setIsConnecting(false); 
        } catch (e) {
            setIsConnecting(false);
            alert(e?.response?.data?.detail);
        }
    }

    useEffect(() => {
        setIsConnected(integrationParams?.credentials ? true : false);
        if (!integrationParams?.credentials) {
            setSelectedEntityType(null);
        }
    }, [integrationParams?.credentials]);

    useEffect(() => {
        if (isConnected && selectedEntityType) {
            setIntegrationParams(prev => ({ ...prev, selectedEntityType: selectedEntityType }));
        }
    }, [selectedEntityType, isConnected, setIntegrationParams]);


    return (
        <>
            <Box sx={{mt: 2}}>
                <Box display='flex' alignItems='center' justifyContent='center' sx={{mt: 2}}>
                    <Button 
                        variant='contained' 
                        onClick={isConnected ? () => {} : handleConnectClick}
                        color={isConnected ? 'success' : 'primary'}
                        disabled={isConnecting}
                        style={{
                            pointerEvents: isConnected ? 'none' : 'auto',
                            cursor: isConnected ? 'default' : 'pointer',
                            opacity: isConnected ? 1 : undefined
                        }}
                    >
                        {isConnected ? 'Hubspot Connected' : isConnecting ? <CircularProgress size={20} /> : 'Connect to Hubspot'}
                    </Button>
                </Box>
            </Box>

            {/* Displays data type selection only if connected */}
            {isConnected && (
                <Box sx={{ mt: 3, width: '100%', maxWidth: 300 }}>
                    <Autocomplete
                        id="hubspot-entity-type"
                        options={entityTypeOptions}
                        value={selectedEntityType}
                        onChange={(event, newValue) => {
                            setSelectedEntityType(newValue);
                        }}
                        renderInput={(params) => <TextField {...params} label="Select Data" />}
                        sx={{ width: '100%' }}
                    />
                </Box>
            )}

            {/* Displays DataForm only if connected and an entity type is selected */}
            {isConnected && selectedEntityType && (
                <Box sx={{mt: 2, width: '100%'}}>
                    <DataForm 
                        integrationType={integrationParams?.type} 
                        credentials={integrationParams?.credentials} 
                        selectedEntityType={selectedEntityType} 
                    />
                </Box>
            )}
        </>
    );
}