from django.shortcuts import render,redirect
from django.http import  JsonResponse
from  django.contrib.auth.decorators import login_required
from home.utils import send_email_to_client
from django.http import HttpResponse
from .forms import ActionForm
from .models import *                                        #for models importing
from .utils import *
import razorpay
from django.http import Http404

# Create your views here.
@login_required(login_url="/login")
def Technoagaaz_Page(request, u_id):            #spoorti land page 
    request.session['form_submitted'] = False
    return render(request,'Technoaagaz.html')

def Technoagaaz_Registrations(request,u_id):         #for selecting the game
    return render(request,'TechnoagaazRegister.html',)

@login_required(login_url="/login")
def info(request,game,u_id):            #for submit the team
    if request.user.is_authenticated and request.user.u_id != u_id:         # Check if the logged-in user has the same u_id as the requested u_id
        raise Http404("You are not authorized to access this page.")
    try:
        if request.method== 'POST':               #for when submit the form
                TeamName=request.POST.get('TeamName')
                LeaderName=request.POST.get('LeaderName')    #for fetch the data when POST request receive
                lEmail=request.POST.get('lEmail')
                phoneNo=request.POST.get('phoneNO')
                team = TechnoagaazTeam.objects.create(          # Create a Team instance
                    teamName=TeamName,
                    leaderName=LeaderName,
                    emailID=lEmail,
                    phoneNO=phoneNo,             #for creating Team object 
                    event='Technoagaaz',
                    game=game,
                )
                user_info = Users_INFO.objects.get(u_id=u_id)   #for assigning user to team// for normal assigning
                team.user = user_info  
                team.save()
                members_data = []
                for i in range(1,15):  # Assuming you have a maximum of 4 members      ###########################
                    member_name = request.POST.get(f'Member{i}Name')
                    if member_name:
                        members_data.append({
                            'name': member_name,               #for appending the member in the list
                        })
                for member_data in members_data:    # Create TeamMember instances #for traversing the  list of dictionary of member
                    TechnoagaazTeamMember.objects.create(
                        team=team,                          #for saving the member in the database row and creating teamMembers object
                        name=member_data['name'],
                    )
                request.session['form_submitted'] = True
                return redirect('TechnoagaazDashboard')
                                
    except Exception as e:                                   
           error_message = str(e)
           return HttpResponse(f'An error occurred: {error_message}', status=500)
          
    context={'game':game,'members':get_member(game)}    
    if request.session.get('form_submitted', False):
        return redirect('landpage') 
    else:
        request.session['form_submitted'] = False
        return render(request,'TechnoagaazRegistration.html',context)
       

@login_required(login_url="/login")
def dashboard(request):
     
    if request.method == 'POST':
        form = ActionForm(request.POST)             # Retrieve data of type of POST request from the POST request 
        if form.is_valid():
            action = form.cleaned_data['action']

            # Proceed with the validated action
            if action == 'paymentDetail':            #for payment details
                # Handle paymentDetail action
                razorpay_payment_id = request.POST.get('razorpay_payment_id')
                razorpay_order_id = request.POST.get('razorpay_order_id')
                razorpay_signature = request.POST.get('razorpay_signature')
                ParamDict={
                    'razorpay_payment_id': razorpay_payment_id,
                    'razorpay_order_id': razorpay_order_id,
                    'razorpay_signature':razorpay_signature
                }
                client = razorpay.Client(auth=("rzp_test_JlKOkCcJe3WrmP", "MAhIirHtHCRL6TckfJb81uhU"))
                try:
                    status = client.utility.verify_payment_signature(ParamDict)
                    team=TechnoagaazTeam.objects.get(order_ID=razorpay_order_id)
                    team.payment_ID = razorpay_payment_id
                    team.payment_signature = razorpay_signature                  #for server side checking
                    team.paid = True
                    team.save()
                    redirect_url = f'/Technoagaaz/TechnoagaazDashboard/'
                    # Redirect on the server side
                    return JsonResponse({'redirect_url': redirect_url})
                except:
                    return render(request,'PaymentStatus.html',{'status':False})
            elif action == 'paymentRequest':          #for payment request
                # Handle paymentRequest action
                team_id = request.POST.get('teamID')
                team=TechnoagaazTeam.objects.get(teamID=team_id)
                original_amount=get_amount(team.game)               #for fetching amount from utils.py
                rozarpay_amount=int(original_amount*100)     
                client=razorpay.Client(auth=("rzp_test_JlKOkCcJe3WrmP", "MAhIirHtHCRL6TckfJb81uhU"))
                payment = client.order.create({'amount':rozarpay_amount, 'currency':'INR', 'payment_capture':'1'})
                team.amount=original_amount
                team.order_ID=payment['id']
                team.save()
                redirect_url = f'/Technoagaaz/TechnoagaazDashboard/&amount={original_amount}&order_id={payment["id"]}'         #for sending data to the ajax request
                return JsonResponse({'redirect_url': redirect_url}) 
        else:
            # Return validation error response
            return JsonResponse({'error': form.errors.get('action', 'Invalid action')}) 
        
    # if request.method == 'POST':
    #     action = request.POST.get('action')            
    #     if action == 'paymentDetail':                  #for payment details
    #         razorpay_payment_id = request.POST.get('razorpay_payment_id')
    #         razorpay_order_id = request.POST.get('razorpay_order_id')
    #         razorpay_signature = request.POST.get('razorpay_signature')
    #         team=Team.objects.get(order_ID=razorpay_order_id)
    #         team.payment_ID = razorpay_payment_id
    #         team.payment_signature = razorpay_signature
    #         team.paid = True
    #         team.save()
    #         redirect_url = f'/Spoorti/SpoortiDashboard/'
    #         # Redirect on the server side
    #         return JsonResponse({'redirect_url': redirect_url})
    #     if action == 'paymentRequest':              
    #         team_id = request.POST.get('teamID')
    #         team=Team.objects.get(teamID=team_id)
    #         original_amount=get_amount(team.game)               #for fetching amount from utils.py
    #         rozarpay_amount=int(original_amount*100)     
    #         client=razorpay.Client(auth=("rzp_test_JlKOkCcJe3WrmP", "MAhIirHtHCRL6TckfJb81uhU"))
    #         payment = client.order.create({'amount':rozarpay_amount, 'currency':'INR', 'payment_capture':'1'})
    #         team.amount=original_amount
    #         team.order_ID=payment['id']
    #         team.save()
    #         redirect_url = f'/Spoorti/SpoortiDashboard/&amount={original_amount}&order_id={payment["id"]}'         #for sending data to the ajax request
    #         return JsonResponse({'redirect_url': redirect_url})  
            
    user_info=request.user
    teams_created_by_user = user_info.created_TechnoagaazTeams.all()
    context={'teamList':teams_created_by_user}
    return render(request,'TechnoagaazDashboard.html',context)
     
     
def delete_team(request,id):
    queryset= TechnoagaazTeam.objects.get(teamID = id)
    queryset.delete()
    return redirect('TechnoagaazDashboard')