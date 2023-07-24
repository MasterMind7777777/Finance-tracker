import React, { useEffect, useState } from 'react';
import { getCategoryList } from '../../api/category';
import { Link } from 'react-router-dom';

export const CategoryList = () => {
    const [categories, setCategories] = useState([]);

    useEffect(() => {
        const fetchCategories = async () => {
            try {
                const response = await getCategoryList();
                setCategories(response);
            } catch (error) {
                console.error(error);
            }
        };
        
        fetchCategories();
    }, []);

    return (
        <div>
            <h2>Category List</h2>
            {categories.map(category =>     
                <div key={category.id}>
                {/* Use the Link component with the URL of the detail page */}
                <Link to={`/categories/${category.id}`}>{category.type} {category.name}</Link>
                </div>
            )}
        </div>
    );
}

export default CategoryList;