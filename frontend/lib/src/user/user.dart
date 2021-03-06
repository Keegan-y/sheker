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
import '../mixin/login_mixin.dart';
import 'package:angular_router/angular_router.dart';

@Component(
  selector: 'user',
  templateUrl: 'user.html',
  directives: [
    formDirectives,
    coreDirectives,
    DeferredContentDirective,
    MaterialButtonComponent,
    MaterialIconComponent,
    MaterialPersistentDrawerDirective,
    MaterialToggleComponent,
    MaterialListComponent,
    MaterialListItemComponent,
  ],
  styleUrls: [
    'package:angular_components/app_layout/layout.scss.css',
  ],
)
class UserComponent with LoginRequired {
  bool customWidth = false;
  bool end = false;
  bool overlay = false;
  Object drawer = null;
  Router _router;
  UserComponent(this._router);

}
