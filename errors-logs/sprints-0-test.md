python -m unittest discover tests/ -v
test_create_session (test_auth_service.TestAuthRepository.test_create_session)
Test creating a session. ... C:\Users\hieuc\Documents\final-project\python-project\src\database\db_helper.py:66: DeprecationWarning: The default datetime adapter is deprecated as of Python 3.12; see the sqlite3 documentation for suggested replacement recipes
cursor = conn.execute(query, params)
ok
test_deactivate_session (test_auth_service.TestAuthRepository.test_deactivate_session)
Test deactivating a session. ... ok
test_get_active_sessions_by_user (test_auth_service.TestAuthRepository.test_get_active_sessions_by_user)
Test getting active sessions for user. ... ok
test_get_failed_attempts_count (test_auth_service.TestAuthRepository.test_get_failed_attempts_count)
Test getting failed attempts count. ... C:\Users\hieuc\Documents\final-project\python-project\src\database\db_helper.py:94: DeprecationWarning: The default datetime adapter is deprecated as of Python 3.12; see the sqlite3 documentation for suggested replacement recipes
cursor = conn.execute(query, params)
FAIL
test_get_session_by_token (test_auth_service.TestAuthRepository.test_get_session_by_token)
Test getting session by token. ... ok
test_is_account_locked (test_auth_service.TestAuthRepository.test_is_account_locked)
Test checking if account is locked. ... FAIL
test_record_login_attempt (test_auth_service.TestAuthRepository.test_record_login_attempt)
Test recording login attempt. ... ok
test_update_session_activity (test_auth_service.TestAuthRepository.test_update_session_activity)
Test updating session activity. ... ok
test_change_password_success (test_auth_service.TestAuthService.test_change_password_success)
Test changing password. ... ERROR
test_change_password_wrong_old (test_auth_service.TestAuthService.test_change_password_wrong_old)
Test changing password with wrong old password. ... ok
test_get_session_info (test_auth_service.TestAuthService.test_get_session_info)
Test getting session info. ... ERROR
test_login_inactive_account (test_auth_service.TestAuthService.test_login_inactive_account)
Test login with inactive account. ... ok
test_login_nonexistent_user (test_auth_service.TestAuthService.test_login_nonexistent_user)
Test login with non-existent user. ... ok
test_login_success (test_auth_service.TestAuthService.test_login_success)
Test successful login. ... ERROR
test_login_wrong_password (test_auth_service.TestAuthService.test_login_wrong_password)
Test login with wrong password. ... ok
test_logout (test_auth_service.TestAuthService.test_logout)
Test logout. ... ERROR
test_logout_all_sessions (test_auth_service.TestAuthService.test_logout_all_sessions)
Test logging out all sessions. ... ERROR
test_password_hashing (test_auth_service.TestAuthService.test_password_hashing)
Test password hashing. ... ok
test_reset_password (test_auth_service.TestAuthService.test_reset_password)
Test resetting password. ... ERROR
test_validate_session_expired (test_auth_service.TestAuthService.test_validate_session_expired)
Test validating an expired session. ... ERROR
test_validate_session_invalid_token (test_auth_service.TestAuthService.test_validate_session_invalid_token)
Test validating an invalid session token. ... ok
test_validate_session_success (test_auth_service.TestAuthService.test_validate_session_success)
Test validating a valid session. ... ERROR
test_account_lockout (test_auth_service.TestIntegrationAuth.test_account_lockout)
Test account lockout after failed attempts. ... ERROR
test_full_login_logout_flow (test_auth_service.TestIntegrationAuth.test_full_login_logout_flow)
Test complete login-logout flow. ... ERROR
test_session_activity_update (test_auth_service.TestIntegrationAuth.test_session_activity_update)
Test session activity is updated on validation. ... ERROR
test_can_delete (test_authorization_service.TestAuthorizationService.test_can_delete)
Test can_delete permission check. ... ok
test_can_edit (test_authorization_service.TestAuthorizationService.test_can_edit)
Test can_edit permission check. ... ok
test_can_view (test_authorization_service.TestAuthorizationService.test_can_view)
Test can_view permission check. ... ok
test_check_permission_raises (test_authorization_service.TestAuthorizationService.test_check_permission_raises)
Test check_permission raises exception. ... ok
test_clear_cache (test_authorization_service.TestAuthorizationService.test_clear_cache)
Test clearing permission cache. ... ok
test_get_permission_matrix (test_authorization_service.TestAuthorizationService.test_get_permission_matrix)
Test getting permission matrix. ... ok
test_get_user_permissions (test_authorization_service.TestAuthorizationService.test_get_user_permissions)
Test getting user permissions. ... ok
test_has_all_permissions (test_authorization_service.TestAuthorizationService.test_has_all_permissions)
Test has_all_permissions method. ... ok
test_has_any_permission (test_authorization_service.TestAuthorizationService.test_has_any_permission)
Test has_any_permission method. ... ok
test_has_permission_admin (test_authorization_service.TestAuthorizationService.test_has_permission_admin)
Test admin has all permissions. ... ok
test_has_permission_sales (test_authorization_service.TestAuthorizationService.test_has_permission_sales)
Test sales has limited permissions. ... ok
test_not_authenticated (test_authorization_service.TestPermissionDecorators.test_not_authenticated)
Test not authenticated error. ... ok
test_require_all_permissions (test_authorization_service.TestPermissionDecorators.test_require_all_permissions)
Test all permissions decorator. ... ok
test_require_any_permission (test_authorization_service.TestPermissionDecorators.test_require_any_permission)
Test any permission decorator. ... ok
test_require_permission_denied (test_authorization_service.TestPermissionDecorators.test_require_permission_denied)
Test permission denied. ... ok
test_require_permission_success (test_authorization_service.TestPermissionDecorators.test_require_permission_success)
Test successful permission check. ... ok
test_accountant_view_only (test_authorization_service.TestPermissionMatrix.test_accountant_view_only)
Test Accountant has view and export only. ... ok
test_admin_has_all_permissions (test_authorization_service.TestPermissionMatrix.test_admin_has_all_permissions)
Test Admin has all permissions. ... ok
test_manager_no_delete_permissions (test_authorization_service.TestPermissionMatrix.test_manager_no_delete_permissions)
Test Manager has no delete permissions. ... ok
test_sales_limited_permissions (test_authorization_service.TestPermissionMatrix.test_sales_limited_permissions)
Test Sales has limited permissions. ... ok
test_get_all (test_authorization_service.TestPermissionRepository.test_get_all)
Test getting all permissions. ... ok
test_get_by_code (test_authorization_service.TestPermissionRepository.test_get_by_code)
Test getting permission by code. ... ok
test_get_by_module (test_authorization_service.TestPermissionRepository.test_get_by_module)
Test getting permissions by module. ... ok
test_get_by_role (test_authorization_service.TestPermissionRepository.test_get_by_role)
Test getting permissions for a role. ... ok
test_get_modules (test_authorization_service.TestPermissionRepository.test_get_modules)
Test getting unique modules. ... ok
test_get_permission_codes_by_role (test_authorization_service.TestPermissionRepository.test_get_permission_codes_by_role)
Test getting permission codes as a set. ... ok
test_assign_and_revoke_permission (test_authorization_service.TestRolePermissionRepository.test_assign_and_revoke_permission)
Test assigning and revoking permissions. ... ok
test_has_all_permissions (test_authorization_service.TestRolePermissionRepository.test_has_all_permissions)
Test checking if role has all permissions. ... ok
test_has_any_permission (test_authorization_service.TestRolePermissionRepository.test_has_any_permission)
Test checking if role has any of the permissions. ... ok
test_has_permission (test_authorization_service.TestRolePermissionRepository.test_has_permission)
Test checking if role has permission. ... ok
test_set_role_permissions (test_authorization_service.TestRolePermissionRepository.test_set_role_permissions)
Test setting all permissions for a role. ... ok
test_empty_ranking (test_kpi_service.TestKPIEdgeCases.test_empty_ranking)
Test ranking with no data. ... ok
test_large_numbers (test_kpi_service.TestKPIEdgeCases.test_large_numbers)
Test with very large numbers. ... ok
test_no_data (test_kpi_service.TestKPIEdgeCases.test_no_data)
Test with no data. ... ok
test_update_existing_kpi (test_kpi_service.TestKPIEdgeCases.test_update_existing_kpi)
Test updating existing KPI record. ... ok
test_zero_target (test_kpi_service.TestKPIEdgeCases.test_zero_target)
Test with zero target. ... ok
test_create_and_get_kpi (test_kpi_service.TestKPIRepository.test_create_and_get_kpi)
Test creating and retrieving KPI record. ... ok
test_get_by_user_and_period (test_kpi_service.TestKPIRepository.test_get_by_user_and_period)
Test getting KPI by user and period. ... ok
test_get_team_average (test_kpi_service.TestKPIRepository.test_get_team_average)
Test getting team average. ... ok
test_get_top_performers (test_kpi_service.TestKPIRepository.test_get_top_performers)
Test getting top performers. ... ok
test_update_rank (test_kpi_service.TestKPIRepository.test_update_rank)
Test updating KPI rank. ... ok
test_calculate_achievement_rate (test_kpi_service.TestKPIService.test_calculate_achievement_rate)
Test achievement rate calculation. ... ok
test_calculate_monthly_kpi (test_kpi_service.TestKPIService.test_calculate_monthly_kpi)
Test monthly KPI calculation. ... ok
test_calculate_overall_score (test_kpi_service.TestKPIService.test_calculate_overall_score)
Test overall score calculation. ... ok
test_compare_with_peers (test_kpi_service.TestKPIService.test_compare_with_peers)
Test peer comparison. ... ok
test_generate_kpi_report (test_kpi_service.TestKPIService.test_generate_kpi_report)
Test KPI report generation. ... Created KPI for month 1: id=1, cars_sold=5
Created KPI for month 2: id=2, cars_sold=10
Created KPI for month 3: id=3, cars_sold=15
Total KPI records: 3
Period: 2024-03, Cars: 15
Period: 2024-02, Cars: 10
Period: 2024-01, Cars: 5
ok
test_get_current_period (test_kpi_service.TestKPIService.test_get_current_period)
Test getting current period. ... ok
test_get_kpi_trend (test_kpi_service.TestKPIService.test_get_kpi_trend)
Test KPI trend retrieval. ... ok
test_get_performance_ranking (test_kpi_service.TestKPIService.test_get_performance_ranking)
Test performance ranking. ... ok
test_get_performance_rating (test_kpi_service.TestKPIService.test_get_performance_rating)
Test performance rating. ... ok
test_get_previous_period (test_kpi_service.TestKPIService.test_get_previous_period)
Test getting previous period. ... ok
test_set_kpi_target (test_kpi_service.TestKPIService.test_set_kpi_target)
Test setting KPI target. ... ok
test_create_and_get_target (test_kpi_service.TestKPITargetRepository.test_create_and_get_target)
Test creating and retrieving target. ... ok
test_get_by_user_and_period (test_kpi_service.TestKPITargetRepository.test_get_by_user_and_period)
Test getting target by user and period. ... ok
test_set_bulk_targets (test_kpi_service.TestKPITargetRepository.test_set_bulk_targets)
Test setting bulk targets. ... ok
test_update_target (test_kpi_service.TestKPITargetRepository.test_update_target)
Test updating target. ... ok
test_database_initialization (test_user_repository.TestDatabaseHelper.test_database_initialization)
Test database is initialized with schema. ... ok
test_execute_and_fetch (test_user_repository.TestDatabaseHelper.test_execute_and_fetch)
Test execute and fetch operations. ... ok
test_fetch_all (test_user_repository.TestDatabaseHelper.test_fetch_all)
Test fetch all operation. ... FAIL
test_create_role (test_user_repository.TestRoleRepository.test_create_role)
Test creating a new role. ... ok
test_delete_role (test_user_repository.TestRoleRepository.test_delete_role)
Test deleting a role. ... ok
test_get_all_roles (test_user_repository.TestRoleRepository.test_get_all_roles)
Test getting all roles. ... FAIL
test_get_role_by_code (test_user_repository.TestRoleRepository.test_get_role_by_code)
Test getting role by code. ... ERROR
test_update_role (test_user_repository.TestRoleRepository.test_update_role)
Test updating a role. ... ok
test_count (test_user_repository.TestUserRepository.test_count)
Test counting users. ... FAIL
test_create_user (test_user_repository.TestUserRepository.test_create_user)
Test creating a new user. ... ok
test_exists (test_user_repository.TestUserRepository.test_exists)
Test checking user existence. ... ok
test_get_by_email (test_user_repository.TestUserRepository.test_get_by_email)
Test getting user by email. ... ok
test_get_by_username (test_user_repository.TestUserRepository.test_get_by_username)
Test getting user by username. ... ok
test_restore_user (test_user_repository.TestUserRepository.test_restore_user)
Test restoring soft-deleted user. ... ok
test_search_users (test_user_repository.TestUserRepository.test_search_users)
Test searching users. ... ok
test_soft_delete (test_user_repository.TestUserRepository.test_soft_delete)
Test soft delete. ... ok
test_update_user (test_user_repository.TestUserRepository.test_update_user)
Test updating user. ... ok
test_create_user_duplicate (test_user_repository.TestUserService.test_create_user_duplicate)
Test creating duplicate user. ... ok
test_create_user_success (test_user_repository.TestUserService.test_create_user_success)
Test successful user creation. ... ok
test_create_user_validation_error (test_user_repository.TestUserService.test_create_user_validation_error)
Test user creation with invalid data. ... ok
test_delete_user_success (test_user_repository.TestUserService.test_delete_user_success)
Test successful user deletion. ... ok
test_get_user_statistics (test_user_repository.TestUserService.test_get_user_statistics)
Test getting user statistics. ... FAIL
test_password_validation (test_user_repository.TestUserService.test_password_validation)
Test password validation. ... ok
test_reset_password (test_user_repository.TestUserService.test_reset_password)
Test password reset. ... ok
test_restore_user (test_user_repository.TestUserService.test_restore_user)
Test restoring deleted user. ... ERROR
test_search_users (test_user_repository.TestUserService.test_search_users)
Test searching users. ... ok
test_update_user_not_found (test_user_repository.TestUserService.test_update_user_not_found)
Test updating non-existent user. ... ok
test_update_user_success (test_user_repository.TestUserService.test_update_user_success)
Test successful user update. ... ok

======================================================================
ERROR: test_change_password_success (test_auth_service.TestAuthService.test_change_password_success)
Test changing password.

---

Traceback (most recent call last):
File "C:\Users\hieuc\Documents\final-project\python-project\tests\test_auth_service.py", line 320, in test_change_password_success
result = self.auth_service.login("changepass", "NewPass123")
File "C:\Users\hieuc\Documents\final-project\python-project\src\services\auth_service.py", line 198, in login
self.user_repo.update_login_info(user.id)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'UserRepository' object has no attribute 'update_login_info'

======================================================================
ERROR: test_get_session_info (test_auth_service.TestAuthService.test_get_session_info)
Test getting session info.

---

Traceback (most recent call last):
File "C:\Users\hieuc\Documents\final-project\python-project\tests\test_auth_service.py", line 361, in test_get_session_info
result = self.auth_service.login("sessioninfo", "TestPass123")
File "C:\Users\hieuc\Documents\final-project\python-project\src\services\auth_service.py", line 198, in login
self.user_repo.update_login_info(user.id)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'UserRepository' object has no attribute 'update_login_info'

======================================================================
ERROR: test_login_success (test_auth_service.TestAuthService.test_login_success)
Test successful login.

---

Traceback (most recent call last):
File "C:\Users\hieuc\Documents\final-project\python-project\tests\test_auth_service.py", line 207, in test_login_success
result = self.auth_service.login("logintest", "TestPass123")
File "C:\Users\hieuc\Documents\final-project\python-project\src\services\auth_service.py", line 198, in login
self.user_repo.update_login_info(user.id)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'UserRepository' object has no attribute 'update_login_info'

======================================================================
ERROR: test_logout (test_auth_service.TestAuthService.test_logout)
Test logout.

---

Traceback (most recent call last):
File "C:\Users\hieuc\Documents\final-project\python-project\tests\test_auth_service.py", line 251, in test_logout
result = self.auth_service.login("logouttest", "TestPass123")
File "C:\Users\hieuc\Documents\final-project\python-project\src\services\auth_service.py", line 198, in login
self.user_repo.update_login_info(user.id)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'UserRepository' object has no attribute 'update_login_info'

======================================================================
ERROR: test_logout_all_sessions (test_auth_service.TestAuthService.test_logout_all_sessions)
Test logging out all sessions.

---

Traceback (most recent call last):
File "C:\Users\hieuc\Documents\final-project\python-project\tests\test_auth_service.py", line 378, in test_logout_all_sessions
result1 = self.auth_service.login("logoutall", "TestPass123")
File "C:\Users\hieuc\Documents\final-project\python-project\src\services\auth_service.py", line 198, in login
self.user_repo.update_login_info(user.id)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'UserRepository' object has no attribute 'update_login_info'

======================================================================
ERROR: test_reset_password (test_auth_service.TestAuthService.test_reset_password)
Test resetting password.

---

Traceback (most recent call last):
File "C:\Users\hieuc\Documents\final-project\python-project\tests\test_auth_service.py", line 350, in test_reset_password
result = self.auth_service.login("resetpass", new_password)
File "C:\Users\hieuc\Documents\final-project\python-project\src\services\auth_service.py", line 198, in login
self.user_repo.update_login_info(user.id)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'UserRepository' object has no attribute 'update_login_info'

======================================================================
ERROR: test_validate_session_expired (test_auth_service.TestAuthService.test_validate_session_expired)
Test validating an expired session.

---

Traceback (most recent call last):
File "C:\Users\hieuc\Documents\final-project\python-project\tests\test_auth_service.py", line 290, in test_validate_session_expired
result = self.auth_service.login("expiredsession", "TestPass123")
File "C:\Users\hieuc\Documents\final-project\python-project\src\services\auth_service.py", line 198, in login
self.user_repo.update_login_info(user.id)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'UserRepository' object has no attribute 'update_login_info'

======================================================================
ERROR: test_validate_session_success (test_auth_service.TestAuthService.test_validate_session_success)
Test validating a valid session.

---

Traceback (most recent call last):
File "C:\Users\hieuc\Documents\final-project\python-project\tests\test_auth_service.py", line 270, in test_validate_session_success
result = self.auth_service.login("validatesession", "TestPass123")
File "C:\Users\hieuc\Documents\final-project\python-project\src\services\auth_service.py", line 198, in login
self.user_repo.update_login_info(user.id)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'UserRepository' object has no attribute 'update_login_info'

======================================================================
ERROR: test_account_lockout (test_auth_service.TestIntegrationAuth.test_account_lockout)
Test account lockout after failed attempts.

---

Traceback (most recent call last):
File "C:\Users\hieuc\Documents\final-project\python-project\tests\test_auth_service.py", line 475, in test_account_lockout
self.auth_service.login("lockout", "CorrectPass123")
~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "C:\Users\hieuc\Documents\final-project\python-project\src\services\auth_service.py", line 198, in login
self.user_repo.update_login_info(user.id)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'UserRepository' object has no attribute 'update_login_info'

======================================================================
ERROR: test_full_login_logout_flow (test_auth_service.TestIntegrationAuth.test_full_login_logout_flow)
Test complete login-logout flow.

---

Traceback (most recent call last):
File "C:\Users\hieuc\Documents\final-project\python-project\tests\test_auth_service.py", line 442, in test_full_login_logout_flow
result = self.auth_service.login("fullflow", "TestPass123")
File "C:\Users\hieuc\Documents\final-project\python-project\src\services\auth_service.py", line 198, in login
self.user_repo.update_login_info(user.id)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'UserRepository' object has no attribute 'update_login_info'

======================================================================
ERROR: test_session_activity_update (test_auth_service.TestIntegrationAuth.test_session_activity_update)
Test session activity is updated on validation.

---

Traceback (most recent call last):
File "C:\Users\hieuc\Documents\final-project\python-project\tests\test_auth_service.py", line 485, in test_session_activity_update
result = self.auth_service.login("activity", "TestPass123")
File "C:\Users\hieuc\Documents\final-project\python-project\src\services\auth_service.py", line 198, in login
self.user_repo.update_login_info(user.id)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'UserRepository' object has no attribute 'update_login_info'

======================================================================
ERROR: test_get_role_by_code (test_user_repository.TestRoleRepository.test_get_role_by_code)
Test getting role by code.

---

Traceback (most recent call last):
File "C:\Users\hieuc\Documents\final-project\python-project\tests\test_user_repository.py", line 111, in test_get_role_by_code
self.role_repo.create(role_data)
~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^
File "C:\Users\hieuc\Documents\final-project\python-project\src\repositories\user_repository.py", line 37, in create
return self.db.execute(query, params)
~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^
File "C:\Users\hieuc\Documents\final-project\python-project\src\database\db_helper.py", line 66, in execute
cursor = conn.execute(query, params)
sqlite3.IntegrityError: UNIQUE constraint failed: roles.role_code

======================================================================
ERROR: test_restore_user (test_user_repository.TestUserService.test_restore_user)
Test restoring deleted user.

---

Traceback (most recent call last):
File "C:\Users\hieuc\Documents\final-project\python-project\tests\test_user_repository.py", line 504, in test_restore_user
restored = self.user_service.restore_user(user.id)
File "C:\Users\hieuc\Documents\final-project\python-project\src\services\user_service.py", line 328, in restore_user
raise UserNotFoundError(f"Không tìm thấy người dùng với ID {user_id}")
src.services.user_service.UserNotFoundError: Không tìm thấy người dùng với ID 2

======================================================================
FAIL: test_get_failed_attempts_count (test_auth_service.TestAuthRepository.test_get_failed_attempts_count)
Test getting failed attempts count.

---

Traceback (most recent call last):
File "C:\Users\hieuc\Documents\final-project\python-project\tests\test_auth_service.py", line 141, in test_get_failed_attempts_count
self.assertEqual(count, 3)
~~~~~~~~~~~~~~~~^^^^^^^^^^
AssertionError: 0 != 3

======================================================================
FAIL: test_is_account_locked (test_auth_service.TestAuthRepository.test_is_account_locked)
Test checking if account is locked.

---

Traceback (most recent call last):
File "C:\Users\hieuc\Documents\final-project\python-project\tests\test_auth_service.py", line 160, in test_is_account_locked
self.assertTrue(is_locked)
~~~~~~~~~~~~~~~^^^^^^^^^^^
AssertionError: False is not true

======================================================================
FAIL: test_fetch_all (test_user_repository.TestDatabaseHelper.test_fetch_all)
Test fetch all operation.

---

Traceback (most recent call last):
File "C:\Users\hieuc\Documents\final-project\python-project\tests\test_user_repository.py", line 68, in test_fetch_all
self.assertEqual(len(results), 2)
~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^
AssertionError: 3 != 2

======================================================================
FAIL: test_get_all_roles (test_user_repository.TestRoleRepository.test_get_all_roles)
Test getting all roles.

---

Traceback (most recent call last):
File "C:\Users\hieuc\Documents\final-project\python-project\tests\test_user_repository.py", line 133, in test_get_all_roles
self.assertEqual(len(roles), 2)
~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^
AssertionError: 6 != 2

======================================================================
FAIL: test_count (test_user_repository.TestUserRepository.test_count)
Test counting users.

---

Traceback (most recent call last):
File "C:\Users\hieuc\Documents\final-project\python-project\tests\test_user_repository.py", line 358, in test_count
self.assertEqual(self.user_repo.count(), 2)
~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 3 != 2

======================================================================
FAIL: test_get_user_statistics (test_user_repository.TestUserService.test_get_user_statistics)
Test getting user statistics.

---

Traceback (most recent call last):
File "C:\Users\hieuc\Documents\final-project\python-project\tests\test_user_repository.py", line 541, in test_get_user_statistics
self.assertEqual(stats["total"], 2)
~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^
AssertionError: 3 != 2

---

Ran 109 tests in 26.213s

FAILED (failures=6, errors=13)
