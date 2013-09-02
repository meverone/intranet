# coding: utf-8
from pyramid.view import view_config

from intranet3.models import DBSession, Client, Project
from intranet3.utils.views import ApiView


@view_config(route_name="api_projects_collection", permission="freelancer",
             renderer='json')
class ProjectsCollection(ApiView):

    def get(self):
        projects = DBSession.query(Project.id, Client.name, Project.name) \
                    .filter(Project.client_id==Client.id) \
                    .filter(Project.active==True) \
                    .order_by(Client.name, Project.name).distinct()
       
        return dict(
            projects=[dict(id=project_id, name=project_name, client_name=client_name, value="%s / %s"% (client_name, project_name))  \
                            for project_id, client_name, project_name in projects]
        )        
