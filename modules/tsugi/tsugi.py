
import re
import pymysql

def get_launch(post_vars,session):
    print extract_post(post_vars)

def get_connection() :
    connection = pymysql.connect(host='localhost',
                             user='ltiuser',
                             port=8889,
                             password='ltipassword',
                             db='tsugi',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

    try:
        with connection.cursor() as cursor:
            # Read a single record
            sql = "SELECT * FROM lti_key"
            cursor.execute(sql)
            result = cursor.fetchone()
            print result
    finally:
        connection.close()

    return connection

def extract_post(post) :
    fixed = dict()
    for (k,v) in post.items():
        if k.startswith('custom_') : 
            nk = k[7:]
            if v.startswith('$') :
                sv = v[1:].lower().replace('.','_')
                if sv == nk : continue
            if nk not in fixed : fixed[nk] = v
        fixed[k] = v

    #print(fixed)
    ret = dict()

    link_key = fixed.get('resource_link_id', None)
    link_key = fixed.get('custom_resource_link_id', link_key)
    ret['link_key'] = link_key

    user_key = fixed.get('person_sourcedid', None)
    user_key = fixed.get('user_id', user_key)
    user_key = fixed.get('custom_user_id', user_key)
    ret['user_key'] = user_key

    context_key = fixed.get('courseoffering_sourcedid', None)
    context_key = fixed.get('context_id', context_key)
    context_key = fixed.get('custom_context_id', context_key)
    ret['context_key'] = context_key

    # LTI 1.x settings and Outcomes
    ret['service'] = fixed.get('lis_outcome_service_url', None)
    ret['sourcedid'] = fixed.get('lis_result_sourcedid', None)

    # LTI 2.x settings and Outcomes
    ret['result_url'] = fixed.get('custom_result_url', None)
    ret['link_settings_url'] = fixed.get('custom_link_settings_url', None)
    ret['context_settings_url'] = fixed.get('custom_context_settings_url', None)

    # LTI 2.x Services
    ret['ext_memberships_id'] = fixed.get('ext_memberships_id', None)
    ret['ext_memberships_url'] = fixed.get('ext_memberships_url', None)
    ret['lineitems_url'] = fixed.get('lineitems_url', None)
    ret['memberships_url'] = fixed.get('memberships_url', None)

    ret['context_title'] = fixed.get('context_title', None)
    ret['link_title'] = fixed.get('resource_link_title', None)

    # Getting email from LTI 1.x and LTI 2.x
    ret['user_email'] = fixed.get('lis_person_contact_email_primary', None)
    ret['user_email'] = fixed.get('custom_person_email_primary', ret['user_email'])

    # Displayname from LTI 2.x
    if ( fixed.get('custom_person_name_full') ) :
        ret['user_displayname'] = fixed['custom_person_name_full']
    elif ( fixed.get('custom_person_name_given') and fixed.get('custom_person_name_family') ) :
        ret['user_displayname'] = fixed['custom_person_name_given']+' '+fixed['custom_person_name_family']
    elif ( fixed.get('custom_person_name_given') ) :
        ret['user_displayname'] = fixed['custom_person_name_given']
    elif ( fixed.get('custom_person_name_family') ) :
        ret['user_displayname'] = fixed['custom_person_name_family']

    # Displayname from LTI 1.x
    elif ( fixed.get('lis_person_name_full') ) :
        ret['user_displayname'] = fixed['lis_person_name_full']
    elif ( fixed.get('lis_person_name_given') and fixed.get('lis_person_name_family') ) :
        ret['user_displayname'] = fixed['lis_person_name_given']+' '+fixed['lis_person_name_family']
    elif ( fixed.get('lis_person_name_given') ) :
        ret['user_displayname'] = fixed['lis_person_name_given']
    elif ( fixed.get('lis_person_name_family') ) :
        ret['user_displayname'] = fixed['lis_person_name_family']

    # Trim out repeated spaces and/or weird whitespace from the user_displayname
    if ( ret.get('user_displayname') ) :
        ret['user_displayname'] = re.sub( '\s+', ' ', ret.get('user_displayname') ).strip()

    # Get the role
    ret['role'] = 0
    roles = ''
    if ( fixed.get('custom_membership_role') ) : # From LTI 2.x
        roles = fixed['custom_membership_role']
    elif ( fixed.get('roles') ) : # From LTI 1.x
        roles = fixed['roles']

    if ( len(roles) > 0 ) :
        roles = roles.lower()
        if ( roles.find('instructor') >=0 ) : ret['role'] = 1000
        if ( roles.find('administrator') >=0 ) : ret['role'] = 5000

    return ret

