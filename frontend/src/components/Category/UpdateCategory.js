import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getCategoryDetail, updateCategory } from '../../api/category';

export const CategoryEdit = () => {
    const { id } = useParams();
    const [name, setName] = useState('');
    const [type, setType] = useState('');
    const navigate = useNavigate();

    useEffect(() => {
        getCategoryDetail(id)
            .then(data => {
                setName(data.name);
                setType(data.type);
            })
            .catch(error => console.error(error));
    }, [id]);

    const handleSubmit = (event) => {
        event.preventDefault();

        updateCategory(id, { name, type })
            .then(() => {
                navigate(`/categories/${id}`);
            })
            .catch(error => console.error(error));
    };

    return (
        <div>
            <h2>Edit Category</h2>
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
                <button type="submit">Update</button>
            </form>
        </div>
    );
};

export default CategoryEdit;
