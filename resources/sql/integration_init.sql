

-- API Description

insert into TBL_API_DESCRIPTION
(id, api_name, api_url, is_enabled, is_mocked, is_log_enabled, bypass_auth, api_description, mocked_response)
values (TBL_API_DESCRIPTION_SEQ.NEXTVAL, 'find_parcel_list_by_centroid', '/parcels/find_parcel_list_by_centroid', 1, 1, 1, 0, '', '{"mocked": "true", "status": "OK"}');

insert into TBL_API_DESCRIPTION
(id, api_name, api_url, is_enabled, is_mocked, is_log_enabled, bypass_auth, api_description, mocked_response)
values (TBL_API_DESCRIPTION_SEQ.NEXTVAL, 'find_parcel_info_by_centroid', '/parcels/find_parcel_info_by_centroid', 1, 0, 1, 0, '', '{"mocked": "true", "status": "OK"}');

insert into TBL_API_DESCRIPTION
(id, api_name, api_url, is_enabled, is_mocked, is_log_enabled, bypass_auth, api_description, mocked_response)
values (TBL_API_DESCRIPTION_SEQ.NEXTVAL, 'find_state_polygon', '/parcels/find_state_polygon', 1, 0, 1, 0, '', '{"mocked": "true", "status": "OK"}');

insert into TBL_API_DESCRIPTION
(id, api_name, api_url, is_enabled, is_mocked, is_log_enabled, bypass_auth, api_description, mocked_response)
values (TBL_API_DESCRIPTION_SEQ.NEXTVAL, 'find_polygon_wrapper_cms', '/parcels/find_polygon_wrapper_cms', 1, 0, 1, 0, '', '{"mocked": "true", "status": "OK"}');

insert into TBL_API_DESCRIPTION
(id, api_name, api_url, is_enabled, is_mocked, is_log_enabled, bypass_auth, api_description, mocked_response)
values (TBL_API_DESCRIPTION_SEQ.NEXTVAL, 'find_overlapping_parcels', '/parcels/find_overlapping_parcels', 1, 0, 1, 0, '', '{"mocked": "true", "status": "OK"}');

insert into TBL_API_DESCRIPTION
(id, api_name, api_url, is_enabled, is_mocked, is_log_enabled, bypass_auth, api_description, mocked_response)
values (TBL_API_DESCRIPTION_SEQ.NEXTVAL, 'docs', '/docs', 1, 0, 1, 1, '', null);

insert into TBL_API_DESCRIPTION
(id, api_name, api_url, is_enabled, is_mocked, is_log_enabled, bypass_auth, api_description, mocked_response)
values (TBL_API_DESCRIPTION_SEQ.NEXTVAL, 'openapi', '/openapi.json', 1, 0, 1, 1, '', null);

insert into TBL_API_DESCRIPTION
(id, api_name, api_url, is_enabled, is_mocked, is_log_enabled, bypass_auth, api_description, mocked_response)
values (TBL_API_DESCRIPTION_SEQ.NEXTVAL, 'find_parcel_request', '/report/find_parcel_request', 1, 0, 1, 0, '', '{"mocked": "true", "status": "OK"}');

insert into TBL_API_DESCRIPTION
(id, api_name, api_url, is_enabled, is_mocked, is_log_enabled, bypass_auth, api_description, mocked_response)
values (TBL_API_DESCRIPTION_SEQ.NEXTVAL, 'find_unit_by_cmd', '/unit/find_unit_by_cmd', 1, 0, 0, 1, '', null);

insert into TBL_API_DESCRIPTION
(id, api_name, api_url, is_enabled, is_mocked, is_log_enabled, bypass_auth, api_description, mocked_response)
values (TBL_API_DESCRIPTION_SEQ.NEXTVAL, 'clear_all_cache', '/platform/clear_all_cache', 1, 0, 0, 1, '', null);


insert into TBL_API_DESCRIPTION
(id, api_name, api_url, is_enabled, is_mocked, is_log_enabled, bypass_auth, api_description, mocked_response)
values (TBL_API_DESCRIPTION_SEQ.NEXTVAL, 'claim_parcel', '/claim/claim_parcel', 1, 0, 1, 0, '', null);


insert into TBL_API_DESCRIPTION
(id, api_name, api_url, is_enabled, is_mocked, is_log_enabled, bypass_auth, api_description, mocked_response)
values (TBL_API_DESCRIPTION_SEQ.NEXTVAL, 'claim_parcel', '/claim/claim_parcel_query', 1, 0, 1, 0, '', null);


-- claims API

insert into TBL_API_DESCRIPTION
(id, api_name, api_url, is_enabled, is_mocked, is_log_enabled, bypass_auth, api_description, mocked_response)
values (TBL_API_DESCRIPTION_SEQ.NEXTVAL, 'register_new_claim', '/claim/register_new_claim', 1, 0, 1, 1, '', null);

insert into TBL_API_DESCRIPTION
(id, api_name, api_url, is_enabled, is_mocked, is_log_enabled, bypass_auth, api_description, mocked_response)
values (TBL_API_DESCRIPTION_SEQ.NEXTVAL, 'assign_surveyor_callback', '/claim/assign_surveyor_callback', 1, 0, 1, 1, '', null);

insert into TBL_API_DESCRIPTION
(id, api_name, api_url, is_enabled, is_mocked, is_log_enabled, bypass_auth, api_description, mocked_response)
values (TBL_API_DESCRIPTION_SEQ.NEXTVAL, 'claim_parcel_survey_query', '/claim/claim_parcel_survey_query', 1, 0, 1, 1, '', null);



-- channels

insert into TBL_CHANNEL (id, auth_key, channel_id, channel_name, description) VALUES
(TBL_CHANNEL_SEQ.NEXTVAL, '812d6c7172d654432817ba6bbf47e95a', '100', 'test', 'test channel'); -- pass: 123

insert into TBL_CHANNEL (id, auth_key, channel_id, channel_name, description) VALUES
(TBL_CHANNEL_SEQ.NEXTVAL, 'dfaea6abf2e6aefa80ef55e1581b56de', '1', 'dispatcher', 'dispatcher channel'); -- pass: 123

insert into TBL_CHANNEL (id, auth_key, channel_id, channel_name, description) VALUES
(TBL_CHANNEL_SEQ.NEXTVAL, 'f140671b458a820c1bd6926ece2724dc', '200', 'saghar', 'saghar channel'); -- pass: 123
