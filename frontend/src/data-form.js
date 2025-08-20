import { useState } from 'react';
import {
    Box,
    TextField,
    Button,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Paper,
    Typography 
} from '@mui/material';
import axios from 'axios';

const endpointMapping = {
    'Notion': 'notion',
    'Airtable': 'airtable',
    'Hubspot': 'hubspot',
};

export const DataForm = ({ integrationType, credentials, selectedEntityType }) => {
    const [loadedData, setLoadedData] = useState(null);
    const [showTable, setShowTable] = useState(false); 
    const endpoint = endpointMapping[integrationType];

    const handleLoad = async () => {
        try {
            const formData = new FormData();
            formData.append('credentials', JSON.stringify(credentials));
            if (integrationType === 'Hubspot' && selectedEntityType) {
                formData.append('entity_type', selectedEntityType);
            }
            const response = await axios.post(`http://localhost:8000/integrations/${endpoint}/load`, formData);
            const data = response.data;
            setLoadedData(data);
            setShowTable(false); 
        } catch (e) {
            alert(e?.response?.data?.detail);
        }
    }

    const handleClearData = () => {
        setLoadedData(null);
        setShowTable(false); 
    };

    const handleExportToTable = () => {
        setShowTable(true); 
    };

    const getTableData = () => {
        if (!loadedData) return { headers: [], rows: [] };

        let dataArray = [];
        let tableTitle = "";

        if (integrationType === 'Hubspot') {
            if (selectedEntityType === 'contacts' && loadedData.contacts) {
                dataArray = loadedData.contacts;
                tableTitle = "HubSpot Contacts";
            } else if (selectedEntityType === 'companies' && loadedData.companies) {
                dataArray = loadedData.companies;
                tableTitle = "HubSpot Companies";
            }
        }

        if (dataArray.length === 0) return { headers: [], rows: [], title: tableTitle };

        const allPropertyKeys = new Set();
        dataArray.forEach(item => {
            if (item.properties) {
                Object.keys(item.properties).forEach(key => allPropertyKeys.add(key));
            }
        });

        const dynamicHeaders = Array.from(allPropertyKeys).sort();
        const headers = ['id', ...dynamicHeaders];

        const rows = dataArray.map(item => {
            const row = { id: item.id }; 
            dynamicHeaders.forEach(header => {
                row[header] = item.properties?.[header] || ''; 
            });
            return row;
        });

        return { headers, rows, title: tableTitle };
    };

    const { headers, rows, title } = getTableData();

    return (
        <Box display='flex' justifyContent='center' alignItems='center' flexDirection='column' width='100%'>
            <Box display='flex' flexDirection='column' width='100%'>
                <TextField
                    label="Loaded Data (Raw JSON)"
                    value={loadedData ? JSON.stringify(loadedData, null, 2) : ''}
                    sx={{mt: 2}}
                    InputLabelProps={{ shrink: true }}
                    disabled
                    multiline
                    rows={10}
                />
                <Button
                    onClick={handleLoad}
                    sx={{mt: 2}}
                    variant='contained'
                >
                    Load Data
                </Button>
                <Button
                    onClick={handleClearData} 
                    sx={{mt: 1}}
                    variant='contained'
                >
                    Clear Data
                </Button>
                {loadedData && ( 
                    <Button
                        onClick={handleExportToTable}
                        sx={{mt: 1}}
                        variant='contained'
                        color='secondary' 
                    >
                        Export to Table
                    </Button>
                )}
            </Box>

            {showTable && loadedData && ( 
                <Box sx={{ mt: 4, width: '100%' }}>
                    <Typography variant="h6" gutterBottom>
                        {title}
                    </Typography>
                    <TableContainer component={Paper}>
                        <Table sx={{ minWidth: 650 }} aria-label="simple table">
                            <TableHead>
                                <TableRow>
                                    {headers.map((header) => (
                                        <TableCell key={header} sx={{ fontWeight: 'bold' }}>
                                            {header.replace(/_/g, ' ').toUpperCase()} {/* Format header names */}
                                        </TableCell>
                                    ))}
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {rows.map((row, index) => (
                                    <TableRow
                                        key={row.id || index} 
                                        sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                                    >
                                        {headers.map((header) => (
                                            <TableCell key={`${row.id}-${header}`}>
                                                {row[header]}
                                            </TableCell>
                                        ))}
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    </TableContainer>
                </Box>
            )}
        </Box>
    );
}