

-- API Description

insert into TBL_API_DESCRIPTION
(api_name, api_url, is_enabled, is_mocked, is_log_enabled, bypass_auth, api_description, mocked_response)
values ('find_parcel_list_by_centroid', '/parcels/find_parcel_list_by_centroid', 1, 1, 1, 0, '', '{"mocked": "true", "status": "OK"}');

insert into TBL_API_DESCRIPTION
(api_name, api_url, is_enabled, is_mocked, is_log_enabled, bypass_auth, api_description, mocked_response)
values ('find_parcel_info_by_centroid', '/parcels/find_parcel_info_by_centroid', 1, 0, 1, 0, '', '{"mocked": "true", "status": "OK"}');

insert into TBL_API_DESCRIPTION
(api_name, api_url, is_enabled, is_mocked, is_log_enabled, bypass_auth, api_description, mocked_response)
values ('find_state_polygon', '/parcels/find_state_polygon', 1, 0, 1, 0, '', '{"mocked": "true", "status": "OK"}');

insert into TBL_API_DESCRIPTION
(api_name, api_url, is_enabled, is_mocked, is_log_enabled, bypass_auth, api_description, mocked_response)
values ('docs', '/docs', 1, 0, 1, 1, '', null);

insert into TBL_API_DESCRIPTION
(api_name, api_url, is_enabled, is_mocked, is_log_enabled, bypass_auth, api_description, mocked_response)
values ('openapi', '/openapi.json', 1, 0, 1, 1, '', null);

insert into TBL_API_DESCRIPTION
(api_name, api_url, is_enabled, is_mocked, is_log_enabled, bypass_auth, api_description, mocked_response)
values ('find_parcel_request', '/report/find_parcel_request', 1, 0, 1, 0, '', '{"mocked": "true", "status": "OK"}');


-- channels

insert into TBL_CHANNEL (auth_key, channel_id, channel_name, description) VALUES
('812d6c7172d654432817ba6bbf47e95a', '100', 'test', 'test channel'); -- pass: 123

insert into TBL_CHANNEL (auth_key, channel_id, channel_name, description) VALUES
('dfaea6abf2e6aefa80ef55e1581b56de', '1', 'dispatcher', 'dispatcher channel'); -- pass: 123
