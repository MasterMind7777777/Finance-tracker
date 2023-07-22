import ListWithAdd from '../Common/ListWithAdd';
import BudgetList from './BudgetList';
import CreateBudget from './CreateBudget';

const BudgetListWithAdd = ListWithAdd(BudgetList, CreateBudget);

export default BudgetListWithAdd;
