from django.shortcuts import render
from .presenters import ChatbotPresenter

def chatbot_view(request):
    response = ""
    if request.method == "POST":
        user_input = request.POST.get("user_input")
        presenter = ChatbotPresenter()
        response = presenter.get_response(user_input)
    
    return render(request, 'chatbot/index.html', {'response': response})

