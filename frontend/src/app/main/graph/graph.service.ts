import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { of, fromEvent } from 'rxjs';
import { map, pluck, tap } from 'rxjs/operators';

import { Node, Edge, Data, Network, DataSet } from 'vis';
import { Friend, UserNode } from '../../../models';
import { AuthService } from 'src/app/auth';

@Injectable()
export class GraphService {

  graphOptions: any = {
    interaction: {
      multiselect: true
    }
  };

  network: Network;
  nodes: UserNode[];
  edges: Friend[];

  constructor(private http: HttpClient, private auth: AuthService) { }

  // server API

  sendFriendRequest(id: string) {
    return this.http.post(`/api/friend/${id}/`, null);
  }

  getNotifications() {
    return this.http.get(`/api/friend/`);
  }

  getFriends() {
    return this.http.get('/api/graph/').pipe(
      tap((friends: {users: UserNode[], friends: Friend[]})=>{
        this.nodes = friends.users;
        this.edges = friends.friends;
      })
    );
  }

  getLevel(level: number) {
    return this.http.get(`/api/graph/${level}/`);
  }


  initializeNetwork(container: HTMLElement) {
    return this.getFriends().pipe(
      tap((res: {users: UserNode[], friends: Friend[]}) => {
        const graphData: Data = {
          nodes: this.nodes, 
          edges: this.edges
        };
        this.network = new Network(container, graphData, this.graphOptions);
        this.network.once('stabilized', ()=>{
          this.network.focus(this.auth.userId, {animation: true});
        });
      })
    );
  }

  makeAllNetwork() {
    return this.getFriends().pipe(
      tap((res: {users: UserNode[], friends: Friend[]}) => {
        const graphData: Data = {
          nodes: res.users, 
          edges: res.friends
        };
        this.network.setData(graphData);
        this.network.once('stabilized', ()=>{
          this.network.focus(this.auth.userId, {animation: true});
        });
      })
    );
  }

  makeLevelNetwork(level: number) {
    return this.getLevel(level).pipe(
      tap((res: {users: UserNode[], friends: Friend[]}) => {
        const graphData: Data = {
          nodes: res.users,
          edges: res.friends
        };
        this.network.setData(graphData);
        this.network.once('stabilized', ()=>{
          this.network.focus(this.auth.userId, {animation: true});
        });
      })
    );
  }

  getClickedNodes() {
    return fromEvent(this.network, 'click').pipe(
      pluck('nodes')
    );
  }

  unselectAll() {
    this.network.unselectAll();
  }

  getUsers(idList: any[]) {
    return this.nodes.filter((user) => idList.includes(user.id));
  }

}
