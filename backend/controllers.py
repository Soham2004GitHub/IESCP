
from flask import Flask
from flask import render_template
from flask import request
from flask import current_app as app #Alias for current running app
from .models import *
from flask import redirect, url_for, jsonify, session
import datetime 
from sqlalchemy import or_, func, asc, desc
import json
#from .models import *

@app.route("/") #base url 127.0.0.1:5000, this is HomePage
def home():
    return render_template("homepage.html")






@app.route("/adminlogin", methods = ["GET", "POST"]) #Admin Login
def admin_login():
    if request.method=="POST":
        uname=request.form.get("uname")
        role="Admin"
        pwd=request.form.get("pwd")
        admin=User.query.filter_by(role=role).first()
        if (uname == admin.user_name and role == admin.role) and pwd == admin.pwd:
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template("adminlogin.html",msg="Sorry! Please Try Again Admin!")
    
    return render_template("adminlogin.html")




@app.route("/userlogin", methods = ["GET", "POST"]) #User Login
def user_login():
    if request.method=="POST":
        uname=request.form.get("uname")
        role=request.form.get("role")
        pwd=request.form.get("pwd")
        user = User.query.filter_by(user_name=uname).first()
        if not user:
            return render_template("userlogin.html" , msg ="Invalid Credentials! Please Try Again!")
        if role == "Influencer":
            influencer = Influencer.query.filter_by(user_id=user.id).first()
            if influencer.flagged == True:
                return render_template("userlogin.html" , msg ="You have been flagged by admin! You cannot login!")
            elif pwd == user.pwd:
                return redirect(url_for("influencer_dashboard", user_id=user.id))
            #elif uname != influencer.user_name:
                #return render_template("userlogin.html" , msg ="Invalid Credentials! Please Try Again!")
            else:
                return render_template("userlogin.html" , msg ="Invalid Credentials! Please Try Again!")
        
        elif role == "Sponsor":
            sponsor = Sponsor.query.filter_by(user_id=user.id).first()
            if sponsor.flagged == True:
                return render_template("userlogin.html" , msg ="You have been flagged by admin! You cannot login!")
            elif pwd == user.pwd:
                return redirect(url_for("sponsor_dashboard", user_id=user.id))
            #elif uname != sponsor.user_name:
                #return render_template("userlogin.html" , msg ="Invalid Credentials! Please Try Again!")
            else:
                return render_template("userlogin.html" , msg ="Invalid Credentials! Please Try Again!")
        
        else:
            return render_template("userlogin.html" , msg ="Invalid Credentials! Please Try Again!")
        
    return render_template("userlogin.html")




@app.route("/adminlogout") #Admin Logout
def admin_logout():
    session.clear()
    return redirect(url_for("admin_login"))

@app.route("/userlogout") #User Logout
def user_logout():
    session.clear()
    return redirect(url_for("user_login"))






@app.route("/admindashboard",methods=["GET","POST"]) #Admin Dashboard
def admin_dashboard():
    campaigns = Campaign.query.filter_by(visibility = "Public", flagged=False, completed="No")
    sponsors = Sponsor.query.filter_by(flagged=False)
    influencers = Influencer.query.filter_by(flagged=False)
    fcampaigns=Campaign.query.filter_by(flagged=True)
    fsponsors=Sponsor.query.filter_by(flagged=True)
    finfluencers = Influencer.query.filter_by(flagged = True)
    return render_template("admindashboard.html", campaigns = campaigns, sponsors = sponsors, fcampaigns=fcampaigns, influencers = influencers, finfluencers = finfluencers, fsponsors = fsponsors)



@app.route("/influnichestats") #Bar Chart - Influencer vs Niche
def influnichestats():
    inf_vs_niche = db.session.query(Influencer.niche, func.count(Influencer.id)).group_by(Influencer.niche).order_by(asc(Influencer.niche)).all()
    data = [{'niche': row[0], 'count': row[1]} for row in inf_vs_niche]
    return jsonify(data)

@app.route("/influplatstats") #Pie Chart - Influencer vs Platform
def influplatstats():
    inf_vs_plat = db.session.query(Influencer.platform, func.count(Influencer.id)).group_by(Influencer.platform).order_by(asc(Influencer.platform)).all()
    data = [{'platform': row[0], 'count': row[1]} for row in inf_vs_plat]
    return jsonify(data)

@app.route("/sponstats") #Bar Chart - Sponsor vs Niche
def sponstats():
    spn_vs_niche = db.session.query(Sponsor.niche, func.count(Sponsor.id)).group_by(Sponsor.niche).order_by(asc(Sponsor.niche)).all()
    data = [{'niche': row[0], 'count': row[1]} for row in spn_vs_niche]
    return jsonify(data)

@app.route("/adminstats") #Overall Stats
def admin_stats():
    inftotal = db.session.query(func.count(Influencer.id)).scalar()
    infflagged = db.session.query(func.count(Influencer.id)).filter(Influencer.flagged == True).scalar()
    highestreachinfluencer = db.session.query(Influencer).order_by(desc(Influencer.reach)).first()
    highestreachname=highestreachinfluencer.user_name
    spntotal = db.session.query(func.count(Sponsor.id)).scalar()
    spnflagged = db.session.query(func.count(Sponsor.id)).filter(Sponsor.flagged == True).scalar()
    cpntotal = db.session.query(func.count(Campaign.id)).filter(Campaign.completed == "No").scalar()
    cpnflagged = db.session.query(func.count(Campaign.id)).filter(Campaign.flagged == True).scalar()
    cpncompleted = db.session.query(func.count(Campaign.id)).filter(Campaign.completed == "Yes").scalar()
    return render_template('adminstats.html', inftotal=inftotal, infflagged=infflagged, highestreachname = highestreachname, spntotal=spntotal, spnflagged=spnflagged, cpntotal=cpntotal, cpnflagged=cpnflagged, cpncompleted=cpncompleted)







@app.route("/admindashboard/cpnflag/<int:id>",methods=["GET","POST"]) #Flag Campaign
def campaign_flag(id):
    campaign=Campaign.query.filter_by(id=id).first()
    campaign.flagged=True
    db.session.commit()
    campaigns = Campaign.query.filter_by(visibility = "Public", flagged=False, completed="No")
    influencers = Influencer.query.filter_by(flagged=False)
    sponsors = Sponsor.query.filter_by(flagged=False)
    fcampaigns=Campaign.query.filter_by(flagged=True)
    fsponsors=Sponsor.query.filter_by(flagged=True)
    finfluencers = Influencer.query.filter_by(flagged = True)
    return render_template("admindashboard.html", campaigns = campaigns, fcampaigns=fcampaigns, influencers = influencers, finfluencers = finfluencers, sponsors = sponsors, fsponsors = fsponsors)






@app.route("/admindashboard/cpnunflag/<int:id>",methods=["GET","POST"]) #Unflag Campaign
def campaign_unflag(id):
    campaign=Campaign.query.filter_by(id=id).first()
    campaign.flagged=False
    db.session.commit()
    campaigns = Campaign.query.filter_by(visibility = "Public", flagged=False, completed="No")
    influencers = Influencer.query.filter_by(flagged=False)
    sponsors = Sponsor.query.filter_by(flagged=False)
    fcampaigns=Campaign.query.filter_by(flagged=True)
    fsponsors=Sponsor.query.filter_by(flagged=True)
    finfluencers = Influencer.query.filter_by(flagged = True)
    return render_template("admindashboard.html", campaigns = campaigns, fcampaigns=fcampaigns, influencers = influencers, finfluencers = finfluencers, sponsors = sponsors, fsponsors = fsponsors)






@app.route("/admindashboard/cpnflagdelete/<int:id>",methods=["GET","POST"]) #Delete Flagged Campaign
def campaign_flagged_delete(id):
    campaign=Campaign.query.filter_by(id=id).first()
    db.session.delete(campaign)
    db.session.commit()
    campaigns = Campaign.query.filter_by(visibility = "Public", flagged=False, completed="No")
    influencers = Influencer.query.filter_by(flagged=False)
    sponsors = Sponsor.query.filter_by(flagged=False)
    fcampaigns=Campaign.query.filter_by(flagged=True)
    fsponsors=Sponsor.query.filter_by(flagged=True)
    finfluencers = Influencer.query.filter_by(flagged = True)
    return render_template("admindashboard.html", campaigns = campaigns, fcampaigns=fcampaigns, influencers = influencers, finfluencers = finfluencers, sponsors = sponsors, fsponsors = fsponsors)




@app.route("/admindashboard/spnflag/<int:id>",methods=["GET","POST"]) #Flag Sponsor
def sponsor_flag(id):
    sponsor=Sponsor.query.filter_by(user_id=id).first()
    sponsor.flagged=True
    db.session.commit()
    campaigns = Campaign.query.filter_by(visibility = "Public", flagged=False, completed="No")
    influencers = Influencer.query.filter_by(flagged=False)
    sponsors = Sponsor.query.filter_by(flagged=False)
    fcampaigns=Campaign.query.filter_by(flagged=True)
    fsponsors=Sponsor.query.filter_by(flagged=True)
    finfluencers = Influencer.query.filter_by(flagged = True)
    return render_template("admindashboard.html", campaigns = campaigns, fcampaigns=fcampaigns, influencers = influencers, finfluencers = finfluencers, sponsors = sponsors, fsponsors = fsponsors)






@app.route("/admindashboard/spnunflag/<int:id>",methods=["GET","POST"]) #Unflag Sponsor
def sponsor_unflag(id):
    sponsor=Sponsor.query.filter_by(user_id=id).first()
    sponsor.flagged=False
    db.session.commit()
    campaigns = Campaign.query.filter_by(visibility = "Public", flagged=False, completed="No")
    influencers = Influencer.query.filter_by(flagged=False)
    sponsors = Sponsor.query.filter_by(flagged=False)
    fcampaigns=Campaign.query.filter_by(flagged=True)
    fsponsors=Sponsor.query.filter_by(flagged=True)
    finfluencers = Influencer.query.filter_by(flagged = True)
    return render_template("admindashboard.html", campaigns = campaigns, fcampaigns=fcampaigns, influencers = influencers, finfluencers = finfluencers, sponsors = sponsors, fsponsors = fsponsors)






@app.route("/admindashboard/spnflagdelete/<int:id>",methods=["GET","POST"]) #Delete Flagged Sponsor
def sponsor_flagged_delete(id):
    sponsor=Sponsor.query.filter_by(user_id=id,flagged=True).first()
    user=User.query.filter_by(id=id).first()
    db.session.delete(sponsor)
    db.session.commit()
    db.session.delete(user)
    db.session.commit()
    campaigns = Campaign.query.filter_by(visibility = "Public", flagged=False, completed="No")
    influencers = Influencer.query.filter_by(flagged=False)
    sponsors = Sponsor.query.filter_by(flagged=False)
    fcampaigns=Campaign.query.filter_by(flagged=True)
    fsponsors=Sponsor.query.filter_by(flagged=True)
    finfluencers = Influencer.query.filter_by(flagged = True)
    return render_template("admindashboard.html", campaigns = campaigns, fcampaigns=fcampaigns, influencers = influencers, finfluencers = finfluencers, sponsors = sponsors, fsponsors = fsponsors)






@app.route("/admindashboard/infflag/<int:id>",methods=["GET","POST"]) #Flag Influencer
def influencer_flag(id):
    influencer=Influencer.query.filter_by(user_id=id).first()
    influencer.flagged=True
    db.session.commit()
    campaigns = Campaign.query.filter_by(visibility = "Public", flagged=False, completed="No")
    influencers = Influencer.query.filter_by(flagged=False)
    sponsors = Sponsor.query.filter_by(flagged=False)
    fcampaigns=Campaign.query.filter_by(flagged=True)
    fsponsors=Sponsor.query.filter_by(flagged=True)
    finfluencers = Influencer.query.filter_by(flagged = True)
    return render_template("admindashboard.html", campaigns = campaigns, fcampaigns=fcampaigns, influencers = influencers, finfluencers = finfluencers, sponsors = sponsors, fsponsors = fsponsors)






@app.route("/admindashboard/infunflag/<int:id>",methods=["GET","POST"]) #Unflag Influencer
def influencer_unflag(id):
    influencer=Influencer.query.filter_by(user_id=id).first()
    influencer.flagged=False
    db.session.commit()
    campaigns = Campaign.query.filter_by(visibility = "Public", flagged=False, completed="No")
    influencers = Influencer.query.filter_by(flagged=False)
    sponsors = Sponsor.query.filter_by(flagged=False)
    fcampaigns=Campaign.query.filter_by(flagged=True)
    fsponsors=Sponsor.query.filter_by(flagged=True)
    finfluencers = Influencer.query.filter_by(flagged = True)
    return render_template("admindashboard.html", campaigns = campaigns, fcampaigns=fcampaigns, influencers = influencers, finfluencers = finfluencers, sponsors = sponsors, fsponsors = fsponsors)





@app.route("/admindashboard/infflagdelete/<int:id>",methods=["GET","POST"]) #Delete Flagged Influencer
def influencer_flagged_delete(id):
    influencer=Influencer.query.filter_by(user_id=id,flagged=True).first()
    user=User.query.filter_by(id=id).first()
    db.session.delete(influencer)
    db.session.commit()
    db.session.delete(user)
    db.session.commit()
    campaigns = Campaign.query.filter_by(visibility = "Public", flagged=False, completed="No")
    influencers = Influencer.query.filter_by(flagged=False)
    sponsors = Sponsor.query.filter_by(flagged=False)
    fcampaigns=Campaign.query.filter_by(flagged=True)
    fsponsors=Sponsor.query.filter_by(flagged=True)
    finfluencers = Influencer.query.filter_by(flagged = True)
    return render_template("admindashboard.html", campaigns = campaigns, fcampaigns=fcampaigns, influencers = influencers, finfluencers = finfluencers, sponsors = sponsors, fsponsors = fsponsors)






@app.route("/sponsorregistration",methods=["GET","POST"])  #Sponsor Registration
def sponsor_register():
    if request.method=="POST":
        uname=request.form.get("uname")
        email=request.form.get("email")
        pwd=request.form.get("pwd")
        niche=request.form.get("niche")
        spr=Sponsor.query.filter_by(user_name=uname).first() 
        if not spr:
            new_user=User(user_name=uname,email=email,pwd=pwd,role="Sponsor",niche=niche)
            db.session.add(new_user)
            db.session.commit()
            new_spr=Sponsor(email=email,user_name=uname,pwd=pwd,niche=niche,user_id=new_user.id)
            db.session.add(new_spr)
            db.session.commit()
            return render_template("sponsorregistration.html",msg="Registration Successful!")
        else:
            return render_template("sponsorregistration.html",msg="Sorry, User is already existed!!")
    
    return render_template("sponsorregistration.html")






@app.route("/influencerregistration",methods=["GET","POST"]) #Influencer Registration
def influencer_register():
    if request.method=="POST":
        uname=request.form.get("uname")
        email=request.form.get("email")
        pwd=request.form.get("pwd")
        niche=request.form.get("niche")
        reach=request.form.get("reach")
        platform=request.form.get("platform")
        ifr=Influencer.query.filter_by(user_name=uname).first() 
        if not ifr:
            new_user=User(user_name=uname,email=email,pwd=pwd,role="Influencer",niche=niche)
            db.session.add(new_user)
            db.session.commit()
            new_ifr=Influencer(email=email,user_name=uname,pwd=pwd,niche=niche,user_id=new_user.id,reach=reach,platform=platform)
            db.session.add(new_ifr)
            db.session.commit()
            return render_template("influencerregistration.html",msg="Registration Successful!")
        else:
            return render_template("influencerregistration.html",msg="Sorry, User is already existed!!")
    
    return render_template("influencerregistration.html")








@app.route("/influencerdashboard/<int:user_id>") #Influencer Dashboard
def influencer_dashboard(user_id):
    influencer=Influencer.query.filter_by(user_id=user_id).first()
    infname=influencer.user_name
    news=Ad_Request.query.filter_by(status="Pending", influencer_id=influencer.id)
    actives=Ad_Request.query.filter_by(status="Accepted", completed="No", influencer_id=influencer.id)
    rejects=Ad_Request.query.filter_by(status="Rejected", influencer_id=influencer.id)
    complete=Ad_Request.query.filter_by(status="Accepted", completed="Yes", influencer_id=influencer.id)
    return render_template("influencerdashboard.html", infname=infname, user_id = user_id, news=news, actives=actives, rejects=rejects, complete=complete)






@app.route("/influencerdashboardfind/<int:user_id>") #Find Page 
def influencer_dashboard_find(user_id):
    influencer=Influencer.query.filter_by(user_id=user_id).first()
    infname=influencer.user_name
    campaigns = Campaign.query.filter_by(visibility = "Public", flagged=False)
    sponsors = Sponsor.query.filter_by(flagged=False)
    cpnrs = Campaign_Request.query.filter_by(influencer_id=influencer.id).all()
    return render_template("influencerdashboardfind.html", infname=infname, user_id = user_id, campaigns=campaigns, sponsors=sponsors, cpnrs = cpnrs)
    

    






@app.route("/influencerdashboardfindcampaigns/<int:user_id>",methods=["GET","POST"]) #Find Campaigns
def influencer_dashboard_find_campaigns(user_id):
    influencer=Influencer.query.filter_by(user_id=user_id).first()
    infname=influencer.user_name
    if request.method == "POST" and 'searchcampaigns' in request.form:
        searchcampaigns = request.form['searchcampaigns']
        by = "%{}%".format(searchcampaigns)
        campaigns = Campaign.query.filter(or_(Campaign.name.like(by), Campaign.niche.like(by)),Campaign.visibility == "Public",Campaign.flagged == False)
        sponsors = Sponsor.query.filter_by(flagged=False)
        cpnrs = Campaign_Request.query.filter_by(influencer_id=influencer.id).all()
        return render_template("influencerdashboardfind.html", infname=infname, user_id = user_id, campaigns=campaigns, sponsors=sponsors, cpnrs = cpnrs, searchcampaigns=searchcampaigns)
        
    

    return render_template("influencerdashboardfind.html", infname=infname, user_id = user_id, campaigns=campaigns, sponsors=sponsors, cpnrs = cpnrs)


@app.route("/influencerdashboardfindrequestcampaign/<int:user_id>/<int:campaign_id>",methods=["GET","POST"]) #Send Ad Request to Sponsors
def send_adrequest_to_sponsor(user_id,campaign_id):
    influencer=Influencer.query.filter_by(user_id=user_id).first()
    infname=influencer.user_name
    campr= Campaign.query.filter_by(id=campaign_id).first()
    campr=Campaign_Request(influencer_id=influencer.id, campaign_id=campr.id, status="Pending")
    db.session.add(campr)
    db.session.commit()
    campaigns = Campaign.query.filter_by(visibility = "Public", flagged=False)
    sponsors = Sponsor.query.filter_by(flagged=False)
    cpnrs = Campaign_Request.query.filter_by(influencer_id=influencer.id).all()
    return render_template("influencerdashboardfind.html", infname=infname, user_id = user_id, campaigns=campaigns, sponsors=sponsors, cpnrs = cpnrs)





@app.route("/influencerdashboardfindsponsors/<int:user_id>",methods=["GET","POST"]) #Find Sponsors
def influencer_dashboard_find_sponsors(user_id):
    influencer=Influencer.query.filter_by(user_id=user_id).first()
    infname=influencer.user_name
    if request.method == "POST" and 'searchsponsors' in request.form:
        searchsponsors = request.form['searchsponsors']
        by = "%{}%".format(searchsponsors)
        sponsors = Sponsor.query.filter(or_(Sponsor.user_name.like(by), Sponsor.niche.like(by)), Sponsor.flagged == False)
        campaigns = Campaign.query.filter_by(visibility = "Public", flagged=False)
        cpnrs = Campaign_Request.query.filter_by(influencer_id=influencer.id).all()
        return render_template("influencerdashboardfind.html", infname=infname, user_id = user_id, campaigns=campaigns, sponsors=sponsors, cpnrs = cpnrs, searchsponsors=searchsponsors)
        
    
    influencer=Influencer.query.filter_by(user_id=user_id).first()
    infname=influencer.user_name
    return render_template("influencerdashboardfind.html", infname=infname, user_id = user_id, campaigns=campaigns, sponsors=sponsors, cpnrs = cpnrs)







@app.route("/influencerdashboard/<int:user_id>/accept/<int:id>",methods=["GET","POST"]) #Accept Ad Request
def accept_adrequest(user_id, id):
    influencer=Influencer.query.filter_by(user_id=user_id).first()
    adr=Ad_Request.query.filter_by(status="Pending", id=id).first()
    adr.status="Accepted"
    adr.completed="No"
    db.session.commit()

    influencer=Influencer.query.filter_by(user_id=user_id).first()
    infname=influencer.user_name
    news=Ad_Request.query.filter_by(status="Pending", influencer_id=influencer.id)
    actives=Ad_Request.query.filter_by(status="Accepted", completed="No", influencer_id=influencer.id)
    rejects=Ad_Request.query.filter_by(status="Rejected", influencer_id=influencer.id)
    complete=Ad_Request.query.filter_by(status="Accepted", completed="Yes", influencer_id=influencer.id)
    return render_template("influencerdashboard.html", infname=infname, user_id = user_id, news=news, actives=actives, rejects=rejects, complete=complete)






@app.route("/influencerdashboard/<int:user_id>/complete/<int:id>",methods=["GET","POST"]) #Mark Ad Request as Complete
def complete_adrequest(user_id, id):
    influencer=Influencer.query.filter_by(user_id=user_id).first()
    adr=Ad_Request.query.filter_by(status="Accepted", id=id).first()
    adr.status="Accepted"
    adr.completed="Yes"
    db.session.commit()

    influencer=Influencer.query.filter_by(user_id=user_id).first()
    infname=influencer.user_name
    news=Ad_Request.query.filter_by(status="Pending", completed="No", influencer_id=influencer.id)
    actives=Ad_Request.query.filter_by(status="Accepted", completed="No", influencer_id=influencer.id)
    rejects=Ad_Request.query.filter_by(status="Rejected", influencer_id=influencer.id)
    complete=Ad_Request.query.filter_by(status="Accepted", completed="Yes", influencer_id=influencer.id)
    return render_template("influencerdashboard.html", infname=infname, user_id = user_id, news=news, actives=actives, rejects=rejects, complete=complete)






@app.route("/influencerdashboard/<int:user_id>/reject/<int:id>",methods=["GET","POST"]) #Reject Ad Request
def reject_adrequest(user_id, id):
    influencer=Influencer.query.filter_by(user_id=user_id).first()
    adr=Ad_Request.query.filter_by(status="Pending", id=id).first()
    adr.status="Rejected"
    db.session.commit()

    influencer=Influencer.query.filter_by(user_id=user_id).first()
    infname=influencer.user_name
    news=Ad_Request.query.filter_by(status="Pending", influencer_id=influencer.id)
    actives=Ad_Request.query.filter_by(status="Accepted", completed="No", influencer_id=influencer.id)
    rejects=Ad_Request.query.filter_by(status="Rejected", influencer_id=influencer.id)
    complete=Ad_Request.query.filter_by(status="Accepted", completed="Yes", influencer_id=influencer.id)
    return render_template("influencerdashboard.html", infname=infname, user_id = user_id, news=news, actives=actives, rejects=rejects, complete=complete)
        





@app.route("/sponsordashboard/<int:user_id>",methods=["GET","POST"]) #Sponsor Dashboard
def sponsor_dashboard(user_id):
    influencers = Influencer.query.all()
    sponsor=Sponsor.query.filter_by(user_id=user_id).first()
    spnname=sponsor.user_name
    campaigns=Campaign.query.filter_by(user_id=user_id, flagged=False)
    return render_template('sponsordashboard.html', spnname=spnname, user_id=user_id, influencers=influencers, campaigns=campaigns)






@app.route("/sponsordashboard/findinfluencers/<int:user_id>",methods=["GET","POST"]) #Find Influencers
def sponsor_dashboard_find_influencers(user_id):
    if request.method == "POST" and 'searchinfluencers' in request.form:
        searchinfluencers = request.form['searchinfluencers']
        by = "%{}%".format(searchinfluencers)
        influencers = Influencer.query.filter(or_(Influencer.user_name.like(by), Influencer.niche.like(by)))
        campaigns = Campaign.query.filter_by(user_id=user_id, flagged=False)
        return render_template("sponsordashboard.html", user_id = user_id, campaigns=campaigns, influencers=influencers, searchinfluencers=searchinfluencers)
    
    sponsor=Sponsor.query.filter_by(user_id=user_id).first()
    spnname=sponsor.user_name
    return render_template("sponsordashboard.html", spnname=spnname, user_id = user_id, influencers=influencers, campaigns=campaigns)








@app.route("/sponsordashboard/campaign/<int:user_id>",methods=["GET","POST"]) #Create Campaign
def add_campaign(user_id):
    if request.method == "POST":
        user = User.query.get(user_id)
        name = request.form.get('name')
        description = request.form.get('description')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
        budget = request.form.get('budget')
        visibility = request.form.get('visibility')
        completed = request.form.get('completed')   
        goals = request.form.get('goals')
        niche = request.form.get('niche')
        campaign = Campaign(name=name,description=description,start_date=start_date,end_date=end_date,budget=budget,visibility=visibility,completed=completed,goals=goals,niche=niche,user_id=user.id)

        db.session.add(campaign)
        db.session.commit()

        return redirect(url_for('add_campaign',user_id=user_id))
    
    sponsor=Sponsor.query.filter_by(user_id=user_id).first()
    spnname=sponsor.user_name
    influencers = Influencer.query.all()
    campaigns = Campaign.query.filter_by(user_id = user_id, flagged=False)
    return render_template('sponsordashboard.html', spnname=spnname, user_id=user_id, campaigns = campaigns, influencers=influencers)







@app.route("/sponsordashboard/campaign/edit/<int:user_id>",methods=["GET","POST"]) #Edit Campaign
def edit_campaign(user_id):
    if request.method == "POST":
        user = User.query.get(user_id)
        new_name = request.form.get('name')
        new_description = request.form.get('description')
        new_start_date = request.form.get('start_date')
        new_end_date = request.form.get('end_date')
        new_start_date = datetime.datetime.strptime(new_start_date, "%Y-%m-%d").date()
        new_end_date = datetime.datetime.strptime(new_end_date, "%Y-%m-%d").date()
        new_budget = request.form.get('budget')
        new_visibility = request.form.get('visibility')
        new_completed = request.form.get('completed')
        new_goals = request.form.get('goals')
        new_niche = request.form.get('niche')

        campaign = Campaign.query.filter_by(user_id=user_id).first()
        campaign.name=new_name
        campaign.description=new_description
        campaign.start_date=new_start_date
        campaign.end_date=new_end_date
        campaign.budget=new_budget
        campaign.visibility=new_visibility
        campaign.completed=new_completed
        campaign.goals=new_goals
        campaign.niche=new_niche
        db.session.commit()

    sponsor=Sponsor.query.filter_by(user_id=user_id).first()
    spnname=sponsor.user_name
    influencers = Influencer.query.all()
    campaigns = Campaign.query.filter_by(user_id = user_id, flagged=False)
    return render_template('sponsordashboard.html', spnname=spnname, user_id=user_id, campaigns = campaigns, influencers=influencers)











@app.route("/sponsordashboard/campaign/delete/<int:user_id>",methods=["GET","POST"]) #Delete Campaign
def delete_campaign(user_id):
    if request.method == "POST":
        old_campaign = Campaign.query.filter_by(user_id=user_id).first()
        db.session.delete(old_campaign)
        db.session.commit()

    sponsor=Sponsor.query.filter_by(user_id=user_id).first()
    spnname=sponsor.user_name
    influencers = Influencer.query.all()
    campaigns = Campaign.query.filter_by(user_id = user_id, flagged=False)
    return render_template('sponsordashboard.html', spnname=spnname, user_id=user_id, campaigns = campaigns, influencers=influencers)








@app.route('/sponsordashboard/campaign/<int:user_id>/<int:campaign_id>/adrequest', methods=['GET', 'POST']) #Show Ad Requests
def ad(user_id, campaign_id):
    user = User.query.get(user_id)
    campaign = Campaign.query.get(campaign_id)
    cid=campaign.id
    ad_requests = Ad_Request.query.filter_by(campaign_id=campaign_id).all()
    sponsor=Sponsor.query.filter_by(user_id=user_id).first()
    spnname=sponsor.user_name
    icpnrs=Campaign_Request.query.filter_by(campaign_id=cid, status="Pending").all()
    return render_template('adrequest.html', spnname=spnname,user_id = user.id, campaign_id=cid, campaign=campaign, ad_requests=ad_requests, icpnrs=icpnrs)



@app.route('/sponsordashboard/campaign/<int:user_id>/<int:campaign_id>/adrequestadrinfaccept/<int:id>', methods=['GET', 'POST']) #Accept Ad Request by Influencers
def adinfaccept(user_id, campaign_id, id):
    user = User.query.get(user_id)
    campaign = Campaign.query.get(campaign_id)
    cid=campaign.id
    campreq=Campaign_Request.query.filter_by(id=id).first()
    campreq.status="Accepted"
    db.session.commit()
    icpnrs=Campaign_Request.query.filter_by(campaign_id=cid, status="Pending").all()
    ad_requests = Ad_Request.query.filter_by(campaign_id=campaign_id).all()
    sponsor=Sponsor.query.filter_by(user_id=user_id).first()
    spnname=sponsor.user_name
    return render_template('adrequest.html', spnname=spnname,user_id = user.id, campaign_id=cid, campaign=campaign, ad_requests=ad_requests, icpnrs=icpnrs)








@app.route('/sponsordashboard/campaign/<int:user_id>/<int:campaign_id>/adrequestadrinfreject/<int:id>', methods=['GET', 'POST']) #Reject Ad Request by Influencers
def adinfreject(user_id, campaign_id, id):
    user = User.query.get(user_id)
    campaign = Campaign.query.get(campaign_id)
    cid=campaign.id
    campreq=Campaign_Request.query.filter_by(id=id).first()
    campreq.status="Rejected"
    db.session.commit()
    icpnrs=Campaign_Request.query.filter_by(campaign_id=cid, status="Pending").all()
    ad_requests = Ad_Request.query.filter_by(campaign_id=campaign_id).all()
    sponsor=Sponsor.query.filter_by(user_id=user_id).first()
    spnname=sponsor.user_name
    return render_template('adrequest.html', spnname=spnname,user_id = user.id, campaign_id=cid, campaign=campaign, ad_requests=ad_requests, icpnrs=icpnrs)


    






@app.route('/sponsordashboard/campaign/<int:user_id>/<int:campaign_id>/addadrequest', methods=['GET', 'POST']) #Add Ad Request
def addadrequest(user_id, campaign_id):
    user = User.query.get(user_id)
    campaign = Campaign.query.get(campaign_id)
    influencers = Influencer.query.all()

    if request.method == 'POST':
        influencer = request.form['influencer']
        infdb = Influencer.query.filter_by(user_name=influencer).first()
        message = request.form['message']
        requirements = request.form['requirements']
        payment = float(request.form['payment'])
        infdb = Influencer.query.get(infdb.id)

        new_request = Ad_Request(
            campaign_id=campaign.id,
            influencer_id=infdb.id,
            messages=message,
            requirements=requirements,
            payment=payment,
            status='Pending',  
            completed="No",
        )
        db.session.add(new_request)
        db.session.commit()
        return redirect(url_for('ad', user_id = user.id, campaign_id=campaign.id))
    
    sponsor=Sponsor.query.filter_by(user_id=user_id).first()
    spnname=sponsor.user_name
    return render_template('addadrequest.html', spnname=spnname, campaign=campaign, influencers=influencers)






@app.route('/sponsordashboard/campaign/<int:user_id>/<int:campaign_id>/editadrequest', methods=['GET','POST']) #Edit Ad Request
def editadrequest(user_id, campaign_id):
    user = User.query.get(user_id)
    influencers = Influencer.query.all()
    campaign = Campaign.query.get(campaign_id)
    if request.method == "POST":
        influencer = request.form['influencer']
        message = request.form['message']
        requirements = request.form['requirements']
        payment = float(request.form['payment'])
        infdb = Influencer.query.filter_by(user_name=influencer).first()
        
        ad_request = Ad_Request.query.filter_by(campaign_id=campaign_id).first()
        ad_request.campaign_id=campaign_id,
        ad_request.influencer_id=infdb.id,
        ad_request.messages=message,
        ad_request.requirements=requirements,
        ad_request.payment=payment,
        ad_request.status='Pending',  
        ad_request.completed=False
        db.session.commit()
        return redirect(url_for('ad', user_id = user.id, campaign_id=campaign.id))
    
    sponsor=Sponsor.query.filter_by(user_id=user_id).first()
    spnname=sponsor.user_name
    campaign = Campaign.query.get(campaign_id)
    return render_template('editadrequest.html', spnname=spnname, campaign=campaign, influencers=influencers)









@app.route('/sponsordashboard/campaign/<int:user_id>/<int:campaign_id>/deleteadrequest', methods=['GET','POST']) #Delete Ad Request
def deleteadrequest(user_id, campaign_id):
    user = User.query.get(user_id)
    campaign = Campaign.query.get(campaign_id)
    if request.method == "POST":
        old_ad_request = Ad_Request.query.filter_by(campaign_id=campaign_id).first()
        db.session.delete(old_ad_request)
        db.session.commit()

        return redirect(url_for('ad', user_id = user.id,  campaign_id=campaign.id))
    
    ad_requests = Ad_Request.query.filter_by(campaign_id=campaign_id).all()
    
    sponsor=Sponsor.query.filter_by(user_id=user_id).first()
    spnname=sponsor.user_name

    return render_template('adrequest.html', spnname=spnname, campaign=campaign, ad_requests=ad_requests)









