import pandas as pd
import numpy as np
import wrangle
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.linear_model import SGDClassifier
from sklearn import preprocessing

#-----------------------------------------------------------------------------

# Model Prep

def dummy_dept(df):
    # dummy dept feature
    dummy_df =  pd.get_dummies(df['dept'])
    # Name the new columns
    dummy_df.columns = ['animal_care_services', 'code_enforcement_services', 
                        'customer_services', 'development_services', 
                        'metro_health', 'parks_and_rec',
                        'solid_waste_management', 'trans_and_cap_improvements', 
                        'unknown_dept']
    # add the dummies to the data frame
    df = pd.concat([df, dummy_df], axis=1)
    return df
#-----------------------------------------------------------------------------    
def dummy_call_reason(df):
    # dummy dept feature
    dummy_df =  pd.get_dummies(df['call_reason'])
    # Name the new columns
    dummy_df.columns = ['buildings', 'business', 'cleanup', 'code',
                        'customer_service', 'field', 'land',
                        'license', 'misc', 'storm', 'streets', 'trades', 
                        'traffic', 'waste']
    # add the dummies to the data frame
    df = pd.concat([df, dummy_df], axis=1)
    return df
#-----------------------------------------------------------------------------
def make_source_id_dummies(df):
    '''This function takes in the cleaned dataframe, makes dummy variables of the source id column, readds the names of the
    dummy columns and returns the concatenated dummy dataframe to the original dataframe.'''
    #make dummies
    dummy_df = pd.get_dummies(df['source_id'])
    #add back column names
    dummy_df.columns = ['web_portal', '311_mobile_app', 'constituent_call', 'internal_services_requests']
    # concatenate dummies to the cleaned data frame
    df = pd.concat([df, dummy_df], axis=1)
    return df

#-------------------------------
def keep_info(df):
    df.drop(df.columns.difference(['dept','call_reason', 'source_id', 'level_of_delay',
                                   'council_district', 'resolution_days_due', 'district_0', 'district_1', 'district_2',
                                   'district_3', 'district_4','district_5', 'district_6', 'district_7', 'district_8', 
                                   'district_9','district_10']), 1, inplace=True)
    return df

#--------------------------------
def model_df():
    '''This function reads in the clean 311 dataframe, applies all of the above functions to prepare it for modeling. 
    The function then returns a cleaned dataframe ready for modeling.'''
    df= wrangle.clean_311(wrangle.get_311_data())
    df= keep_info(df)
    df= dummy_dept(df)
    df= dummy_call_reason(df)
    df= make_source_id_dummies(df)

    return df
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def split(df, stratify_by= 'level_of_delay'):
    """
    Crude train, validate, test split
    To stratify, send in a column name
    """
    if stratify_by == None:
        train, test = train_test_split(df, test_size=.2, random_state=319)
        train, validate = train_test_split(train, test_size=.3, random_state=319)
    else:
        train, test = train_test_split(df, test_size=.2, random_state=319, stratify=df[stratify_by])
        train, validate = train_test_split(train, test_size=.3, random_state=319, stratify=train[stratify_by])
    return train, validate, test


#------------------------------------
def separate_y(train, validate, test):
    '''
    This function will take the train, validate, and test dataframes and separate the target variable into its
    own panda series
    '''
    
    X_train = train.drop(columns=['level_of_delay'])
    y_train = train.level_of_delay
    X_validate = validate.drop(columns=['level_of_delay'])
    y_validate = validate.level_of_delay
    X_test = test.drop(columns=['level_of_delay'])
    y_test = test.level_of_delay
    return X_train, y_train, X_validate, y_validate, X_test, y_test
#------------------------------------
def scale_data(X_train, X_validate, X_test):
    '''
    This function will scale numeric data using Min Max transform after 
    it has already been split into train, validate, and test.
    '''
    
    
    obj_col = []
    num_train = X_train.drop(columns = obj_col)
    num_validate = X_validate.drop(columns = obj_col)
    num_test = X_test.drop(columns = obj_col)
    
    
    # Make the thing
    scaler = preprocessing.MinMaxScaler()
    
   
    # we only .fit on the training data
    scaler.fit(num_train)
    train_scaled = scaler.transform(num_train)
    validate_scaled = scaler.transform(num_validate)
    test_scaled = scaler.transform(num_test)
    
    # turn the numpy arrays into dataframes
    train_scaled = pd.DataFrame(train_scaled, columns=num_train.columns)
    validate_scaled = pd.DataFrame(validate_scaled, columns=num_train.columns)
    test_scaled = pd.DataFrame(test_scaled, columns=num_train.columns)
    
    
    return train_scaled, validate_scaled, test_scaled

#------------------------------------

def split_separate_scale(df, stratify_by= 'level_of_delay'):
    '''
    This function will take in a dataframe
    separate the dataframe into train, validate, and test dataframes
    separate the target variable from train, validate and test
    then it will scale the numeric variables in train, validate, and test
    finally it will return all dataframes individually
    '''
    
    # split data into train, validate, test
    train, validate, test = split(df, stratify_by= 'level_of_delay')
    
     # seperate target variable
    X_train, y_train, X_validate, y_validate, X_test, y_test = separate_y(train, validate, test)
    
    
    # scale numeric variable
    train_scaled, validate_scaled, test_scaled = scale_data(X_train, X_validate, X_test)
    
    return train, validate, test, X_train, y_train, X_validate, y_validate, X_test, y_test, train_scaled, validate_scaled, test_scaled
