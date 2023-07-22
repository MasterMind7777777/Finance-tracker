import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createCategory } from '../../api/category';

export const CategoryCreate = () => {
    const [name, setName] = useState('');
    const [type, setType] = useState('');
    const navigate = useNavigate();

    const handleSubmit = (event) => {
        event.preventDefault();

        createCategory({ name, type })
            .then(() => {
                navigate('/categories');
            })
            .catch(error => console.error(error));
    };

    return (
        <div>
            <h2>Create Category</h2>
            <form onSubmit={handleSubmit}>
                <label>
                    Name:
                    <input
                        type="text"
                        value={name}
                        onChange={e => setName(e.target.value)}
                    />
                </label>
                <label>
                    Type:
                    <input
                        type="text"
                        value={type}
                        onChange={e => setType(e.target.value)}
                    />
                </label>
                <button type="submit">Create</button>
            </form>
        </div>
    );
};

export default CategoryCreate;
