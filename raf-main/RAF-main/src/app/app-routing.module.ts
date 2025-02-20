import { NgModule } from "@angular/core";
import { RouterModule, Routes } from "@angular/router";
import { RafScoreComponent} from "./raf-score/raf-score.component";
import { NavbarComponent } from "./navbar/navbar.component";
import { HomeComponent } from "./home/home.component";
import { LoginComponent } from "./login/login.component";


const routes: Routes = [
    {path:'', component:HomeComponent},
    {path: "raf-score", component:RafScoreComponent},
    {path:'login', component: LoginComponent}
]


@NgModule({
    imports: [RouterModule.forRoot(routes)],
    exports:[RouterModule],
})

export class AppRoutingModule {}