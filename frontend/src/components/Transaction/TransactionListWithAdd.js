import ListWithAdd from '../Common/ListWithAdd';
import TransactionList from './TransactionList';
import AddTransaction from './AddTransaction';

const TransactionListWithAdd = ListWithAdd(TransactionList, AddTransaction);

export default TransactionListWithAdd;
