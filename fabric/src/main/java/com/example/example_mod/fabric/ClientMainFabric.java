package com.example.example_mod.fabric;

import net.fabricmc.api.ClientModInitializer;

import com.example.example_mod.ClientMain;

public final class ClientMainFabric implements ClientModInitializer {
    @Override
    public void onInitializeClient() {

        ClientMain.init();

    }

}
