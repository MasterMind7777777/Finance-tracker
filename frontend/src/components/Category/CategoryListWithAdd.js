import ListWithAdd from '../Common/ListWithAdd';
import CategoryList from './CategoryList';
import AddCategory from './AddCategory';

const CategoryListWithAdd = ListWithAdd(CategoryList, AddCategory);

export default CategoryListWithAdd;
