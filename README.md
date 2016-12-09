# Flask Super Seed 

Flask Seed is a production ready seed app with following plugins integrated.

  - Flask Admin
  - Flask Security
  - Flask User
  - Flask RestFul
  - Flask Marshmallow
  - Flask Script
  - Flask Migrate

### Using the seed:
  - Create Models
  - Create Schemas for the model
  - Define Resources for your schema's and model's
  - Define value for following in your resource
     - model = None
     - schema = None
      -  filters = {}
      -  fields = ()
      -  max_limit = 100
      -  default_limit = 20
      -  related_resource = {}
      -  order_by = []
      -  only = ()
      -  exclude = ()
      - auth_required = False/True
        - roles_accepted = () `access if any of these roles assigned to user`
        - roles_required = () `access if all of these roles assigned to user`
  -  Define View for your resource
     - Add methods to api_methods in your view (BulkUpdate, List, Fetch, Create, Delete, Update)
     - View are of 2 types Base and Association View.
     - Base view supports (BulkUpdate, List, Fetch, Create, Delete, Update) 
       - BulkUpdate `PUT update single or multiple resource`
       - Save `POST save single or multiple resource`
       - Update `PATCH update single resource`
       - List `GET fetch multiple resource`
       - Fetch `GET fetch single resource`
     - AssociationView for Association table to create, delete or update relation among Resources using Patch call.


### Example

#### User Model

```sh
class User(db.Model, BaseMixin, UserMixin, ReprMixin):
    email = db.Column(db.String(127), unique=True, nullable=False)
    password = db.Column(db.String(255), default='', nullable=False)
    username = db.Column(db.String(127), nullable=True)

    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    last_login_at = db.Column(db.DateTime())
    current_login_at = db.Column(db.DateTime())

    last_login_ip = db.Column(db.String(45))
    current_login_ip = db.Column(db.String(45))
    login_count = db.Column(db.Integer)
    roles = db.relationship('UserRole', back_populates='user')

    user_profile = db.relationship("UserProfile", uselist=False, back_populates="user", cascade='all, delete-orphan')

    @hybrid_property
    def name(self):
        if self.user_profile and self.user_profile.first_name:
            if self.user_profile.last_name:
                return self.user_profile.first_name + self.user_profile.last_name
            return self.user_profile.first_name

```
### Role Model

```sh

class Role(db.Model, RoleMixin, ReprMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    users = db.relationship('UserRole', back_populates='role')


```
### UserRole Model

```sh

class UserRole(db.Model, BaseMixin):

    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('role.id', ondelete='CASCADE'))

    user = db.relationship('User', back_populates='roles')
    role = db.relationship('Role', back_populates='users')

    UniqueConstraint(user_id, role_id)

```
### Schemas

```sh
class UserSchema(BaseSchema):

    class Meta:
        model = User
        exclude = ('created_on', 'updated_on', 'password', 'current_login_at', 'current_login_ip',
                   'last_login_at', 'last_login_ip', 'login_count')

    id = ma.Integer(dump_only=True)
    email = ma.Email(unique=True, primary_key=True, required=True)
    username = ma.String(required=True)
    user_profile = ma.Nested('UserProfileSchema', load=True, many=False, exclude=('user',))
    roles = ma.Nested('RoleSchema', many=True, dump_only=True)
```


### Resources

```sh

class UserResource(ModelResource):

    model = User
    schema = UserSchema

    filters = {
        'username': [ops.Equal, ops.Contains],
        'active': [ops.Boolean]
    }

    related_resource = {
        'user_profile': UserProfileResource
    }

    order_by = ['email', 'id']

    only = ()

    exclude = ()

    def has_read_permission(self, request, qs):
        return qs

    def has_change_permission(self, request, obj):
        return True

    def has_delete_permission(self, request, obj):
        return True

    def has_add_permission(self, request, obj):

        return True

```

### View
```sh

@api.register()
class UserListView(BaseView):
    resource = UserResource
    
    
@api.register()
class UserRoleAssociationView(AssociationView):

    resource = UserRoleResource

```

This will create following resource's
- /user/<slug>/
    - GET /user/1/
    -     Get single instance of resource
    - PATCH /user/1/
    -     Update single instance of resource
    - Delete /user/1/
    -     Delete single instance of resource
- /user/
    - GET /user/
    -     Get multiple instance of resource
    - POST /user/
    -      Create multiple or single instance of resource
    - PUT /user/
    -      Update multiple or single instance of resource
- /user_role/
    -  Patch /user_role/
    -     Patch multiple association among resource
        -   Example:
            -  [ {"user_id":1,"role_id":1, "__action": "add"}, {"user_id":1,"role_id":1, "__action": "remove"}]