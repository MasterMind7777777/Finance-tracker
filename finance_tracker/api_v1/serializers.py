from rest_framework import serializers
from budgets.models import CategoryBudget
from analytics.models import FinancialHealth
from transactions.models import TransactionSplit
from transactions.models import Category, Transaction
from capital.models import SavingGoal
from users.models import User, UserProfile, SocialMediaAccount, FriendRequest

class CategoryBudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryBudget
        fields = ['id', 'category', 'budget_limit']
        read_only_fields = ['id']

    def create(self, validated_data):
        user = self.context['request'].user
        category_budget = CategoryBudget.objects.create(**validated_data)
        category_budget.user.set([user])
        return category_budget

    def validate_category(self, value):
        # check if the category belongs to the current user
        if value.user != self.context['request'].user:
            raise serializers.ValidationError("You do not have access to this category.")
        return value

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'

class FinancialHealthSerializer(serializers.ModelSerializer):
    advice = serializers.SerializerMethodField()

    class Meta:
        model = FinancialHealth
        fields = ('user', 'income', 'expenditure', 'savings', 'investments', 'advice', 'score')

    def get_advice(self, obj):
        if obj.advice:
            return obj.advice.split('\n')
        return []

    def to_internal_value(self, data):
        ret = super().to_internal_value(data)
        if data.get('advice'):
            ret['advice'] = '\n'.join(data['advice'])
        return ret

class SavingGoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavingGoal
        fields = ['id', 'creator', 'users', 'name', 'description', 'target_amount', 'target_date', 'categories', 'current_amount']
        read_only_fields = ['current_amount', 'creator']

    def validate_categories(self, categories):
        # Check that each category belongs to the user making the request.
        for category in categories:
            if category.user != self.context['request'].user:
                raise serializers.ValidationError("You can only add or remove your own categories.")
        return categories
    

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('id', 'user', 'bio', 'profile_picture')


class SocialMediaAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialMediaAccount
        fields = ('id', 'platform', 'username')

    def validate(self, data):
        # Grab the user from the context
        user = self.context.get('user')
        if not user:
            raise serializers.ValidationError("User does not exist.")
        return data

    def create(self, validated_data):
        # Grab the user from the context and add to the validated_data
        user = self.context.get('user')
        return SocialMediaAccount.objects.create(user=user, **validated_data)



class FriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ('id', 'from_user', 'to_user', 'created_at', 'accepted')


class UserSerializer(serializers.ModelSerializer):
    userprofile = UserProfileSerializer(read_only=True)
    socialmediaaccount_set = SocialMediaAccountSerializer(many=True, read_only=True)
    sent_friend_requests = FriendRequestSerializer(many=True, read_only=True)
    received_friend_requests = FriendRequestSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'phone_number', 'date_of_birth', 'userprofile', 'socialmediaaccount_set',
                  'sent_friend_requests', 'received_friend_requests')

class TransactionSplitSerializer(serializers.ModelSerializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        model = TransactionSplit
        fields = ['id', 'requester', 'requestee', 'transaction', 'amount', 'status']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['amount'] = float(representation['amount'])
        return representation
