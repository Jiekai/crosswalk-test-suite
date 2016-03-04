Feature: wrt-ux-app
 Scenario: Crosswalk WebApp Terminated TaskManager
  When launch "web_feature_notification_tests"
    And I should see title "Web Features Test: web_feature_notification_tests"
    And I press "home" hardware key
   Then I press "recent" hardware key
    And I swipe view "description=web_feature_notification_tests" to "left"
    And I wait 3 seconds
    And I should not see view "description=web_feature_notification_tests"
    And I press "home" hardware key
