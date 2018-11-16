import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { of, fromEvent } from 'rxjs';
import { map, pluck, tap } from 'rxjs/operators';

import { Node, Edge, Data, Network, DataSet } from 'vis';
import { User, Friend } from '../../../models';
import { AuthService } from 'src/app/auth';

@Injectable()
export class GraphService {

  graphOptions: any = {
    interaction: {
      multiselect: true
    }
  };

  network: Network;
  nodes;
  edges;

  users;

  constructor(private http: HttpClient, private auth: AuthService) { }

  // server API

  getFriends() {
    return this.http.get('/api/friend').pipe(
      tap((friends: any)=>{
        console.log('friends:', friends);
        this.users = friends.users;
      })
    );
  }

  getLevel(level: number) {
    return this.http.get(`/api/friend/${level}/`).pipe(
      tap((friends: any)=>{
        console.log(`level ${level} friends:`, friends);
        this.users = friends.users;
      })
    );
  }


  initializeNetwork(container: HTMLElement) {
    return this.getFriends().pipe(
      tap((res: {users: User[], friends: Friend[]}) => {
        console.log('u', res.users)
        console.log('f', res.friends)
        this.nodes = res.users; 
        this.edges = res.friends;
        const graphData: Data = {
          nodes: this.nodes, 
          edges: this.edges
        };
        this.network = new Network(container, graphData, this.graphOptions);
        // focus not working for some reason
        // this.network.focus(this.auth.userId, {animation: true});
      })
    );
  }

  makeAllNetwork() {
    return this.getFriends().pipe(
      tap((res: {users: User[], friends: Friend[]}) => {
        this.nodes = res.users; 
        this.edges = res.friends;
        const graphData: Data = {
          nodes: this.nodes, 
          edges: this.edges
        };
        this.network.setData(graphData);
        // focus not working for some reason
        this.network.focus(this.auth.userId, {animation: true});
      })
    );
  }

  makeLevelNetwork(level: number) {
    return this.getLevel(level).pipe(
      tap((res: {users: User[], friends: Friend[]}) => {
        this.nodes = res.users; 
        this.edges = res.friends;
        const graphData: Data = {
          nodes: this.nodes, 
          edges: this.edges
        };
        this.network.setData(graphData);
        // focus not working for some reason
        this.network.focus(this.auth.userId, {animation: true});
      })
    );
  }

  getClikedNodes() {
    return fromEvent(this.network, 'click').pipe(
      pluck('nodes')
    );
  }

  unselectAll() {
    this.network.unselectAll();
  }

  getUsers(idList: any[]) {
    return this.users.filter((user) => idList.includes(user.id));
  }

}
