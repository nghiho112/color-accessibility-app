'use client';

import { Button } from 'react-bootstrap';
import React, { useState } from 'react';
import { baseUrl } from '../constants';

export default function Landing({ sendPhase }) {
    const [image, setImage] = useState(null);

    const [fileTest, setFileTest] = useState(null);

    const handleChange = (e) => {
        console.log(e.target.files);
        const file = e.target.files[0];
        setImage(file);

        setFileTest({ name: file.name, type: file.type });
    };

    const handleUpload = () => {
        if (image) {
            console.log('Uploading file:', image);
        } else {
            console.log('Please select a file');
        }

        const formData = new FormData();
        formData.append('file', image);

        fetch(`${baseUrl}files/`, {
            mode: 'cors',
            method: 'POST',
            headers: {
                'Content-Type': 'application/json', // change to multiform/data
            },
            body: JSON.stringify(fileTest), // test with fileName and fileType
        })
            .then((response) => {
                console.log(response);
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json(); // or response.text() if the response is not JSON
            })
            .then((data) => {
                console.log(data);
            })
            .catch((error) => {
                console.error(
                    'There was a problem with the fetch operation:',
                    error
                );
            });

        sendPhase({
            phase: 'integration',
            file: image,
        });
    };
    return (
        <div>
            <div className="box">
                <input
                    type="file"
                    accept="image/*"
                    onChange={handleChange}
                />
            </div>
            <Button
                className="upload"
                style={{ backgroundColor: '#39545B' }}
                onClick={handleUpload}
            >
                GENERATE
            </Button>
        </div>
    );
}
