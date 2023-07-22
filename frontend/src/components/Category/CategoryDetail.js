import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getCategoryDetail, deleteCategory as apiDeleteCategory } from '../../api/category';

export const CategoryDetail = () => {
    const { id } = useParams();
    const [category, setCategory] = useState(null);
    const navigate = useNavigate();

    useEffect(() => {
        getCategoryDetail(id)
            .then(data => setCategory(data))
            .catch(error => console.error(error));
    }, [id]);

    const deleteCategory = () => {
        apiDeleteCategory(id)
            .then(() => {
                navigate('/categories'); // Or whatever path you'd like to redirect to
            })
            .catch(error => console.error(error));
    };

    if (!category) {
        return <div>Loading...</div>;
    }

    return (
        <div>
            <h2>Category Detail</h2>
            <p>{category.id}</p>
            <p>{category.name}</p>
            <p>{category.type}</p>
            <button onClick={deleteCategory}>Delete Category</button>
        </div>
    );
}

export default CategoryDetail;
