import 'dart:convert';
import 'package:angular_router/angular_router.dart';
import 'package:angular/angular.dart';
import 'package:angular_forms/angular_forms.dart';
import 'package:angular_components/angular_components.dart';
import 'package:angular_components/app_layout/material_persistent_drawer.dart';
import 'package:angular_components/content/deferred_content.dart';
import 'package:angular_components/material_button/material_button.dart';
import 'package:angular_components/material_icon/material_icon.dart';
import 'package:angular_components/material_list/material_list.dart';
import 'package:angular_components/material_list/material_list_item.dart';
import 'package:angular_components/material_toggle/material_toggle.dart';

import 'src/routes.dart';

import 'src/service/http.dart';

@Component(selector: 'my-app', templateUrl: 'app_component.html', directives: [
  routerDirectives,
], styleUrls: [
  'package:angular_components/app_layout/layout.scss.css',
], exports: [
  RoutePaths,
  Routes
])
class AppComponent {
  final Router _router;

  MessageManager mm;

  AppComponent(this._router) {
    initWs();
  }

  void initWs() {
    mm = MessageManager((event) async {
      dynamic data = jsonDecode(event.data);
      if (data['message']['type'] == 'sys') {
        if (data['message']['code'] == 401) {
          // await requireLogin();
        }
      }
    });
  }

  Future<NavigationResult> requireLogin() async {
    return _router.navigate(Routes.userLogin.toUrl());
  }
}
