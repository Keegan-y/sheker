import 'package:angular_router/angular_router.dart';

import 'route_paths.dart';
import 'chat/room.template.dart' as room_template;
import 'chat/users.template.dart' as users_template;
import 'user/user.template.dart' as user_template;
import 'user/user_edit.template.dart' as user_edit_template;
import 'user/user_login.template.dart' as user_login_template;
import 'user/user_regist.template.dart' as user_regist_template;

export 'route_paths.dart';

class Routes {
  static final room = RouteDefinition(
      routePath: RoutePaths.room,
      component: room_template.RoomComponentNgFactory);

  static final users = RouteDefinition(
      routePath: RoutePaths.users,
      component: users_template.UsersComponentNgFactory);

  static final user = RouteDefinition(
      routePath: RoutePaths.user,
      component: user_template.UserComponentNgFactory);

  static final userEdit = RouteDefinition(
      routePath: RoutePaths.userEdit,
      component: user_edit_template.UserEditComponentNgFactory);

  static final userLogin = RouteDefinition(
      routePath: RoutePaths.userLogin,
      component: user_login_template.UserLoginComponentNgFactory);

  static final userRegist = RouteDefinition(
      routePath: RoutePaths.userEdit,
      component: user_regist_template.UserRegistComponentNgFactory);

  static final all = <RouteDefinition>[
    room,
    users,
    user,
    userEdit,
    userLogin,
    userRegist,
    RouteDefinition.redirect(
      path: '',
      redirectTo: RoutePaths.room.toUrl(),
    ),
  ];
}
