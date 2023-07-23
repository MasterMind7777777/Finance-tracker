import React, { useState } from 'react';
import { bulkUploadTransactions } from '../../api/transaction';
import { toast } from 'react-toastify';

const TransactionBulkUpload = () => {
    const [selectedFile, setSelectedFile] = useState(null);

    const fileHandler = event => {
        setSelectedFile(event.target.files[0]);
    }

    const fileUploadHandler = async () => {
        if (!selectedFile) {
            toast.error("No file selected!");
            return;
        }
    
        try {
            // Initial upload
            let response = await bulkUploadTransactions(selectedFile);
            console.log(response);
    
            if (typeof response === 'object' && response.status) {
                switch (response.status) {
                    case 'Pending':
                        toast.info('Upload successful, transactions are being processed...');
                        break;
                    case 'Error':
                        toast.error(`Upload failed: ${response.message}`);
                        break;
                    case 'Complete':
                        toast.success(response.message);
                        return; // If Complete on first attempt, return
                    default:
                        toast.error('Unexpected status received. Please try again.');
                        break;
                }
            } else {
                toast.error('Upload failed. Please try again.');
                return;
            }
    
            // If not Complete, keep checking status every 5 seconds
            const intervalId = setInterval(async () => {
                response = await bulkUploadTransactions(selectedFile); // Function to check status needs to be implemented
                
                console.log(response);
                if (response.status === 'Complete') {
                    clearInterval(intervalId);
                    toast.success(response.message);
                }
            }, 200);
            
        } catch (error) {
            toast.error(`An error occurred: ${error.message}`);
        }
    }

    return (
        <div>
            <input type="file" onChange={fileHandler} />
            <button onClick={fileUploadHandler}>Upload</button>
        </div>
    );
}

export default TransactionBulkUpload;
