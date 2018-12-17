import { Component, OnInit } from '@angular/core';
import { SearchService } from './search.service';
import { map } from 'rxjs/operators';
import { User } from '../../../models';

@Component({
  selector: 'app-search',
  templateUrl: './search.component.html',
  styleUrls: ['./search.component.css']
})
export class SearchComponent implements OnInit {

  searchTerm: string = '';
  showResult: boolean = false;
  profiles: any[] = [];

  constructor(private search: SearchService) { }

  ngOnInit() {
  }

  searchUser() {
    this.search.search(this.searchTerm).pipe(
      map((rawResult: any)=>{
        return rawResult.persons.map((rawUserInfo) => { 
          return {
            ...rawUserInfo,
            firstName: rawUserInfo.first_name,
            lastName: rawUserInfo.last_name
          };
        });
      })
    ).subscribe((searchResult: User[])=>{
      this.profiles = searchResult;
      this.showResult = true;
    });
  }

  cancelSearch() {
    this.showResult = false;
    this.searchTerm = '';
  }

}
