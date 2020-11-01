import 'dart:html';

import 'package:angular_app/src/routes.dart';
import 'package:angular_router/angular_router.dart';
import 'package:angular_router/angular_router.dart';

mixin LoginRequired {
  Router _router;
  Future<bool> canNavigate() async {
    bool loginFlag = window.localStorage.containsKey('login');
    print(loginFlag);
    if (loginFlag) {
      return true;
    } else {
      print('redi');
      _router.navigate(Routes.userLogin.toUrl());
      return false;
    }
  }
}
