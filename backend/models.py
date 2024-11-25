from flask_sqlalchemy import SQLAlchemy

db=SQLAlchemy() #Instance of SQLAlchemy

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer,primary_key=True)
    user_name = db.Column(db.String,unique=True,nullable=False)
    email = db.Column(db.String,nullable=False)
    pwd = db.Column(db.String,nullable=False)
    role = db.Column(db.String,nullable=False)
    niche = db.Column(db.String, nullable=False)
    influencer=db.relationship("Influencer",backref="user")
    sponsor=db.relationship("Sponsor",backref="user")
    campaign=db.relationship("Campaign",backref="user")

class Influencer(db.Model):
    __tablename__="influencer"
    id = db.Column(db.Integer,primary_key=True)
    user_name = db.Column(db.String,unique=True,nullable=False)
    email = db.Column(db.String,nullable=False)
    pwd = db.Column(db.String,nullable=False)
    niche = db.Column(db.String, nullable=False)
    reach = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer,db.ForeignKey("user.id"))
    platform = db.Column(db.String, nullable=False)
    flagged = db.Column(db.Boolean,default=False)
    ad_request = db.relationship("Ad_Request", backref="influencer")
    campaign_request = db.relationship("Campaign_Request", backref="influencer")


class Sponsor(db.Model):
    __tablename__ = "sponsor"
    id = db.Column(db.Integer,primary_key=True)
    user_name = db.Column(db.String,unique=True,nullable=False)
    email = db.Column(db.String,nullable=False)
    pwd = db.Column(db.String,nullable=False)
    niche = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer,db.ForeignKey("user.id"),nullable=False)
    flagged = db.Column(db.Boolean,default=False)


class Campaign(db.Model):
    __tablename__ = "campaign"
    id = db.Column(db.Integer,primary_key=True,unique=True,nullable=False)
    name = db.Column(db.String,nullable=False)
    description = db.Column(db.Text,nullable=False)
    start_date = db.Column(db.DateTime,nullable=False)
    end_date = db.Column(db.DateTime,nullable=False)
    budget = db.Column(db.Float, nullable=False)
    visibility = db.Column(db.String,default="Public")
    goals = db.Column(db.Text,nullable=False)
    user_id = db.Column(db.Integer,db.ForeignKey("user.id"),nullable=False)
    niche = db.Column(db.String, nullable=False)
    completed = db.Column(db.String,default="No")
    flagged = db.Column(db.Boolean,default=False)
    ad_request = db.relationship("Ad_Request", backref="campaign")
    campaign_request = db.relationship("Campaign_Request", backref="campaign")
    
class Ad_Request(db.Model):
    __tablename__ = "ad_request"
    id = db.Column(db.Integer,primary_key=True,unique=True,nullable=False)
    campaign_id = db.Column(db.Integer,db.ForeignKey("campaign.id"),nullable=False)
    influencer_id = db.Column(db.Integer,db.ForeignKey("influencer.id"),nullable=False)
    messages = db.Column(db.Text)
    requirements = db.Column(db.Text, nullable=False)
    payment = db.Column(db.Float, nullable=False)
    status = db.Column(db.String, nullable=False)
    completed = db.Column(db.String,default="No")

class Campaign_Request(db.Model):
    __tablename__ = "campaign_request"
    id = db.Column(db.Integer,primary_key=True,unique=True,nullable=False)
    campaign_id = db.Column(db.Integer,db.ForeignKey("campaign.id"),nullable=False)
    influencer_id = db.Column(db.Integer,db.ForeignKey("influencer.id"),nullable=False)
    status = db.Column(db.String, nullable=False)